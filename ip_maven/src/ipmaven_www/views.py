from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import F, IntegerField
from django.db.models.functions import Length
from .models import Whois, Mapping, UploadedFile
from .serializers import WhoisSerializer, MappingSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import pandas as pd
from pathlib import Path
from django.db import connection
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.paginator import Paginator
import psycopg2
from django.db.models import Q
import logging
import os, re, json
from django.utils import timezone
from ipaddress import ip_address, AddressValueError
import subprocess
import socket

logger = logging.getLogger("logger")

"""internet connected?"""
def is_connected():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

def perform_whois_lookup(ip):
    if not is_connected():
        print("No internet connection. Skipping WHOIS lookup.")
        return None

    try:
        result = subprocess.run(["whois", ip], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return result.stdout
        else:
            print(f"WHOIS lookup failed for {ip} with return code {result.returncode}")
            return None
    except Exception as e:
        print(f"WHOIS lookup error: {e}")
        return None

def is_integer(value):
    try:
        int(value)
        return True
    except ValueError:
        return False

def DBConnect():
    try:
        # Access the 'default' database configuration from settings
        db_config = settings.DATABASES['default']

        # Create a PostgreSQL connection using the configuration details
        conn = psycopg2.connect(
            dbname=db_config['NAME'],
            user=db_config['USER'],
            password=db_config.get('PASSWORD', ''),
            host=db_config.get('HOST', 'localhost'),
            port=db_config.get('PORT', '5432')
        )
    except Exception as err:
        print(err)
        logging.exception(err)
        sys.exit(1)
    return conn

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def help(request):
    return render(request, 'help.html')

def mappings(request):
    return render(request, 'mappings.html')

def whois(request):
    return render(request, 'whois.html')

def detail(request, detail):
    return render(request, 'detail.html', {'detail': detail})

def configure(request):
    return render(request, 'configure.html')

def process_file(file_path, replace):
    try:
        print(f'TRYING TO POST MAPPINGS WITH FILE PATH {file_path} and REPLACE {replace}')
        db_path = connection.settings_dict['NAME']
        
        conn = DBConnect()
        cursor = conn.cursor()

        try:
            if replace == 'true':
                # delete all objects if user wants to replace
                Mapping.objects.all().delete()
        except Exception as e:
            pass;
        
        logger = logging.getLogger('ipmaven_www')

        file_path = Path(settings.BASE_DIR) / 'ipmaven_www' / 'data' / 'in' / file_path

        # is file a log file or text file?
        if file_path.suffix == '.txt':
            print("processing text file")

            ct = 0
            #load text file by line
            with open(file_path, 'r') as f:
                for l in f:
                    ct = ct + 1
                    # Extract data fields from JSON object
                    query = l
                    answer = l
                    score = 0

                    # Check if record already exists
                    cursor.execute("""
                        SELECT 1 FROM ipmaven_www_mapping
                        WHERE query = %s AND answer = %s
                    """, (query, answer))
                    exists = cursor.fetchone()

                    # Insert record if it does not already exist
                    if not exists:
                        cursor.execute("""
                            INSERT INTO ipmaven_www_mapping (
                                query, answer, score
                            ) VALUES (%s, %s, %s)
                        """, (query, answer, score))

            r = f"{ct} rows processed successfully"

        else:
            print("processing log file")
        
            df = pd.read_csv(file_path, sep='\t', names=['data'], header=None)
            
            r = f"{df.count} rows processed successfully"

            for index, row in df.iterrows():
                data = json.loads(row['data'])

                # Extract data fields from JSON object
                query = data.get('query')
                answer = data.get('answers', [""])[0]
                orig_ip = data.get('id', {}).get('orig_h')
                orig_port = data.get('id', {}).get('orig_p')
                resp_ip = data.get('id', {}).get('resp_h')
                resp_port = data.get('id', {}).get('resp_p')
                proto = data.get('proto')
                rtt = data.get('rtt')
                query_class = data.get('qclass_name')
                query_type = data.get('qtype_name')
                response_code = data.get('rcode_name')
                score = 0

                if query_type != 'A': # TODO: just store IV4 addresses right now
                    continue

                # Check if record already exists
                cursor.execute("""
                    SELECT 1 FROM ipmaven_www_mapping
                    WHERE query = %s AND answer = %s
                """, (query, answer))
                exists = cursor.fetchone()

                # Insert record if it does not already exist
                if not exists:
                    cursor.execute("""
                        INSERT INTO ipmaven_www_mapping (
                            query, answer, orig_ip, orig_port, resp_ip, resp_port, proto, rtt, query_class, query_type, response_code, score
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (query, answer, orig_ip, orig_port, resp_ip, resp_port, proto, rtt, query_class, query_type, response_code, score))

        conn.commit()
        logger.info(f'File {file_path} processed successfully')

    except Exception as e:
        r = f"ERROR: {e}"
        print(e)
    finally:
        # Close the connection
        cursor.close()
        conn.close()

    return r

class Pagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class LogsApiView(APIView):
    @swagger_auto_schema(
        operation_summary="Get server logs"
    )
    def get(self, request):
        log_file_path = os.path.join(settings.BASE_DIR, 'app.log')

        logs = []
        # Regex pattern to match the logging format, excluding milliseconds
        log_pattern = re.compile(r'(?P<level>INFO)\s+(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d{3}\s+(?P<source>\S+)\s+(?P<message>.+)')

        try:
            with open(log_file_path, 'r') as log_file:
                for line in log_file:
                    match = log_pattern.match(line)
                    if match:
                        # Extract timestamp without milliseconds
                        timestamp = match.group('timestamp')
                        logs.append({
                            'level': match.group('level'),
                            'timestamp': timestamp,
                            'source': match.group('source'),
                            'message': match.group('message'),
                        })

        except FileNotFoundError:
            return JsonResponse({"error": "Log file not found."}, status=404)

        return JsonResponse({"logs": logs})


class StatsApiView(APIView):
    @swagger_auto_schema(
        operation_summary="Get overall server stats"
    )
    def get(self, request):
        mappings_count = Mapping.objects.count()
        whois_count = Whois.objects.count()

        return Response({
            "whois": whois_count,
            "mappings": mappings_count
        })
        
class MappingApiView(APIView):
    @swagger_auto_schema(
        operation_summary="Processes new file",
        operation_description="Processing new mapping file",
        manual_parameters=[
            openapi.Parameter('file_path', openapi.IN_QUERY, description="File to process", type=openapi.TYPE_STRING),
            openapi.Parameter('replace', openapi.IN_QUERY, description="Whether to replace (True) or append (False)", type=openapi.TYPE_STRING)
        ]
    )
    def post(self, request):
        # Retrieve the file path from the query parameter
        file_path = request.query_params.get('file_path')
        replace = request.query_params.get('replace', 'false')

        r = process_file(file_path, replace)

        return Response(r)
        
    @swagger_auto_schema(
        operation_summary="Gets all mappings",
        operation_description="Gets all mappings in the system, with optional search and pagination",
        manual_parameters=[
            openapi.Parameter('search_query', openapi.IN_QUERY, description="Search query", type=openapi.TYPE_STRING),
            openapi.Parameter('search_by', openapi.IN_QUERY, description="Search by", type=openapi.TYPE_STRING),
            openapi.Parameter('page_number', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Page size", type=openapi.TYPE_INTEGER),
        ]
    )
    def get(self, request):
        # Get query parameters
        raw_search_by = request.query_params.get('search_by', '')
        raw_search_query = request.query_params.get('search_query', '')
        page_number = request.query_params.get('page_number', 1)
        page_size = request.query_params.get('page_size', 100)
        requires_all = request.query_params.get('requires_all', 'False')

        # Filter records based on search query
        mappings_search_parameters = Mapping.objects.first().parameters()
        search_by_list = raw_search_by.split(',') if raw_search_by else []
        search_query_list = raw_search_query.split(',') if raw_search_query else []

        num_search_bys = len(search_by_list)
        num_search_queries = len(search_query_list)

        # Validate search_by fields
        for search_by in search_by_list:
            if search_by not in mappings_search_parameters:
                return Response(
                    {'error': f'Invalid search by field \'{search_by}\' for Whois.'},
                    status=400
                )

        # Prepare the queryset of all Whois objects
        q_object = Q()

        # 1 search query, no search by --> search on everything
        if num_search_bys == 0 and num_search_queries == 1:
            queryset = Mapping.objects.select_related('query_whois', 'answer_whois').all()
            for search_by in mappings_search_parameters:
                if search_by not in ['registration_date', 'update_date', 'updated']:
                    q_object |= Q(**{f'{search_by}__icontains': search_query_list[0]})

        # 1 search query, multiple search bys --> search on the search bys
        elif num_search_bys > 1 and num_search_queries == 1:
            queryset = Mapping.objects.select_related('query_whois', 'answer_whois').only(*search_by_list)
            for search_by in search_by_list:
                q_object |= Q(**{f'{search_by}__icontains': search_query_list[0]})

        # n search queries, n search bys --> search by pair
        elif num_search_bys == num_search_queries:
            queryset = Mapping.objects.select_related('query_whois', 'answer_whois').only(*search_by_list)
            requires_all = eval(requires_all.capitalize())
            for search_by, search_query in zip(search_by_list, search_query_list):
                search_args = {f'{search_by}__icontains': search_query}
                if requires_all:
                    q_object &= Q(**search_args)
                else:
                    q_object |= Q(**search_args)

        else:
            return Response(
                {"error": "Number of 'search_by' fields must match the number of 'search_query' fields."},
                status=400
            )
        
        # Filter the queryset using the dynamically constructed Q object
        queryset = queryset.filter(q_object).order_by('id')

        if queryset.count() < 1:
            print(f"Creating new mapping for {raw_search_query}")

            print(f"Creating new mapping for {raw_search_query}")

            whois_record = None

            query_ip = None
            try:
                # full valid IP address?
                try:
                    query_ip = ip_address(raw_search_query)
                except Exception:
                    pass

                # already have a Whois record?
                whois_record = Whois.objects.filter(
                    start_address__lte=raw_search_query,
                    end_address__gte=raw_search_query
                ).first()

                # if no existing Whois record, perform real-time
                print(whois_record)
                if not whois_record:
                    print("doing whois")
                    whois_data = perform_whois_lookup(raw_search_query)
                    if whois_data:
                        print(f"whois: {whois_data}")
                        parsed_data = {
                            "start_address": raw_search_query,
                            "end_address": raw_search_query,
                            "name": "Unknown",  # todo
                            "handle": "Unknown",  # todo
                            "customer_name": "Unknown",  # todo
                            "score": 0,
                            "updated": timezone.now()
                        }
                        whois_record = Whois.objects.create(**parsed_data)

            except AddressValueError:
                print("h3")
                query_ip = None

            if query_ip:
                new_mapping = Mapping.objects.create(
                    answer=raw_search_query,
                    answer_whois=whois_record,
                    query_type="A",
                    query_class="IN",
                    response_code="NOERROR",
                    score=0,
                    updated=timezone.now(),
                    created=timezone.now()
                )

                queryset = Mapping.objects.filter(id=new_mapping.id)

        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page_number)

        # Build the response including related Whois records
        items = []
        for obj in page_obj.object_list:
            item = {
                "id": obj.id,
                "query": obj.query,
                "answer": obj.answer,
                "query_whois": {
                    "id": obj.query_whois.id,
                    "name": obj.query_whois.name,
                    "handle": obj.query_whois.handle,
                    "start_address": obj.query_whois.start_address,
                    "end_address": obj.query_whois.end_address,
                    "customer_name": obj.query_whois.customer_name,
                    "street_address": obj.query_whois.street_address,
                    "city": obj.query_whois.city,
                    "state": obj.query_whois.state,
                    "postal_code": obj.query_whois.postal_code,
                    "code2": obj.query_whois.code2,
                    "org_handle": obj.query_whois.org_handle,
                    "parent_org_handle": obj.query_whois.parent_org_handle,
                    "referral_server": obj.query_whois.referral_server,
                    "registration_date": obj.query_whois.registration_date,
                    "update_date": obj.query_whois.update_date
                } if obj.query_whois else None,
                "answer_whois": {
                    "id": obj.answer_whois.id,
                    "name": obj.answer_whois.name,
                    "handle": obj.answer_whois.handle,
                    "start_address": obj.answer_whois.start_address,
                    "end_address": obj.answer_whois.end_address,
                    "customer_name": obj.answer_whois.customer_name,
                    "street_address": obj.answer_whois.street_address,
                    "city": obj.answer_whois.city,
                    "state": obj.answer_whois.state,
                    "postal_code": obj.answer_whois.postal_code,
                    "code2": obj.answer_whois.code2,
                    "org_handle": obj.answer_whois.org_handle,
                    "parent_org_handle": obj.answer_whois.parent_org_handle,
                    "referral_server": obj.answer_whois.referral_server,
                    "registration_date": obj.answer_whois.registration_date,
                    "update_date": obj.answer_whois.update_date
                } if obj.answer_whois else None,
                "timestamp": obj.timestamp,
                "uid": obj.uid,
                "orig_ip": obj.orig_ip,
                "orig_port": obj.orig_port,
                "resp_ip": obj.resp_ip,
                "resp_port": obj.resp_port,
                "proto": obj.proto,
                "query_type": obj.query_type,
                "query_class": obj.query_class,
                "response_code": obj.response_code,
                "rtt": obj.rtt,
                "rejected": obj.rejected,
                "AA": obj.AA,
                "TC": obj.TC,
                "RD": obj.RD,
                "RA": obj.RA,
                "name": obj.name,
                "handle": obj.handle,
                "start_address": obj.start_address,
                "end_address": obj.end_address,
                "created": obj.created,
                "updated": obj.updated,
                "score": obj.score
            }
            items.append(item)

        response_data = {
            'items': items,
            'totalPages': paginator.num_pages,
            'pageNumber': page_obj.number
        }

        return Response(response_data)

class WhoisApiView(APIView):
    @swagger_auto_schema(
        operation_summary="Gets all whois records",
        operation_description="Gets all whois records in the system, with optional search and pagination",
        manual_parameters=[
            openapi.Parameter('search_query', openapi.IN_QUERY, description="Search query", type=openapi.TYPE_STRING),
            openapi.Parameter('search_by', openapi.IN_QUERY, description="Search by", type=openapi.TYPE_STRING),
            openapi.Parameter('page_number', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Page size", type=openapi.TYPE_INTEGER),
            openapi.Parameter('requires_all', openapi.IN_QUERY, description="Requires all", type=openapi.TYPE_STRING),
        ]
    )
    def get(self, request):
        # Get query parameters
        raw_search_by = request.query_params.get('search_by', '')
        raw_search_query = request.query_params.get('search_query', '')
        page_number = int(request.query_params.get('page_number', 1))
        page_size = int(request.query_params.get('page_size', 100))
        requires_all = request.query_params.get('requires_all', 'False').lower() == 'true'

        filters = Q(name__icontains=raw_search_query) | \
          Q(handle__icontains=raw_search_query) | \
          Q(customer_name__icontains=raw_search_query) | \
          (Q(start_address__icontains=raw_search_query) & Q(start_len__lte=15)) | \
          (Q(end_address__icontains=raw_search_query) & Q(end_len__lte=15))

        if is_integer(raw_search_query):
            filters |= Q(id=int(raw_search_query))  # Ensure it's converted to int

        queryset = Whois.objects.annotate(
            start_len=Length('start_address', output_field=IntegerField()),
            end_len=Length('end_address', output_field=IntegerField())
        ).filter(filters).order_by('customer_name')


        print(queryset.query)

        # Pagination
        # paginator = Paginator(queryset, page_size, allow_empty_first_page=True)
        # page_obj = paginator.get_page(page_number)

        response_data = {
            #'items': list(page_obj.object_list.values()),
            'items': list(queryset.order_by('-id').values()),
            'totalPages': 1,
            'pageNumber': 1,
            #'totalPages': paginator.num_pages,
            #'pageNumber': page_obj.number,
            'query_params': {'search_query': raw_search_query}
        }

        return Response(response_data)

def configure(request):
    uploaded_files = UploadedFile.objects.all().order_by('-upload_time')
    return render(request, 'configure.html', {'uploaded_files': uploaded_files})

def upload_log_file(request):
    if request.method == 'POST' and 'logFile' in request.FILES:
        log_file = request.FILES['logFile']
        save_path = os.path.join(settings.MEDIA_ROOT, log_file.name)

        try:
            # Save file to the specified directory
            with default_storage.open(save_path, 'wb+') as destination:
                for chunk in log_file.chunks():
                    destination.write(chunk)

            # Log the upload success
            UploadedFile.objects.create(
                filename=log_file.name,
                status='Successful'
            )
        except Exception as e:
            # Log the upload failure
            UploadedFile.objects.create(
                filename=log_file.name,
                status='Failed'
            )

        process_file(log_file.name, True)

        uploaded_files = UploadedFile.objects.all().order_by('-upload_time')
        return render(request, 'configure.html', {'uploaded_files': uploaded_files})

    return render(request, 'upload_template.html')