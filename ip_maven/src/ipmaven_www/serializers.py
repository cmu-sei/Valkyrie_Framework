from rest_framework import serializers
from .models import Mapping, Whois

class MappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mapping
        fields = [
            'id', 
            'query', 
            'answer', 
            'query_whois', 
            'answer_whois', 
            'name', 
            'handle', 
            'start_address', 
            'end_address', 
            'created', 
            'updated',
            'timestamp',
            'uid',
            'orig_ip',
            'orig_port',
            'resp_ip',
            'resp_port',
            'proto',
            'query_type',
            'query_class',
            'response_code',
            'rtt',
            'rejected',
            'AA',
            'TC',
            'RD',
            'RA',
            'score'
        ]

class WhoisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Whois
        fields = [
            'id', 'end_address', 'handle', 'name', 'org_handle', 'start_address', 'ref',
            'city', 'code2', 'code3', 'customer_name', 'e164', 'customer', 'postal_code',
            'registration_date', 'state', 'street_address', 'update_date', 'comment',
            'referral_server', 'parent_org_handle', 'updated'
        ]