from django.db import models
from datetime import datetime

class UploadedFile(models.Model):
    filename = models.CharField(max_length=255)
    upload_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)

    def __str__(self):
        return self.filename

class Whois(models.Model):
    end_address = models.CharField(max_length=255, db_index=True)
    handle = models.CharField(max_length=255)
    name = models.CharField(max_length=255, db_index=True)
    org_handle = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    start_address = models.CharField(max_length=255, db_index=True)
    ref = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    code2 = models.CharField(max_length=2, null=True, blank=True, db_index=True)
    code3 = models.CharField(max_length=3, null=True, blank=True)
    customer_name = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    e164 = models.CharField(max_length=255, null=True, blank=True)
    customer = models.CharField(max_length=255, null=True, blank=True)
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    registration_date = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    street_address = models.CharField(max_length=255, null=True, blank=True)
    update_date = models.CharField(max_length=50, null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    referral_server = models.CharField(max_length=255, null=True, blank=True)
    parent_org_handle = models.CharField(max_length=255, null=True, blank=True)
    updated = models.DateTimeField(default=datetime.utcnow)

    def __str__(self):
        return self.name

    def parameters(self):
        params = list(self.__dict__.keys())
        # python dictionaries may hidden _state key
        # but that is an invalid parameter so we remove it
        if '_state' in params: params.remove('_state')
        return params

class Mapping(models.Model):
    query = models.CharField(max_length=255)
    answer = models.CharField(max_length=255)

    query_whois = models.ForeignKey(Whois, related_name='mappings_as_query', on_delete=models.SET_NULL, null=True)
    answer_whois = models.ForeignKey(Whois, related_name='mappings_as_answer', on_delete=models.SET_NULL, null=True)

    # Additional fields from Zeek DNS records
    timestamp = models.FloatField(null=True, blank=True)  # 'ts'
    uid = models.CharField(max_length=100, null=True, blank=True)  # Unique identifier

    orig_ip = models.GenericIPAddressField(null=True, blank=True)  # 'id.orig_h'
    orig_port = models.IntegerField(null=True, blank=True)  # 'id.orig_p'
    resp_ip = models.GenericIPAddressField(null=True, blank=True)  # 'id.resp_h'
    resp_port = models.IntegerField(null=True, blank=True)  # 'id.resp_p'

    proto = models.CharField(max_length=10, null=True, blank=True)  # 'proto'
    query_type = models.CharField(max_length=50, null=True, blank=True)  # 'qtype_name'
    query_class = models.CharField(max_length=50, null=True, blank=True) # 'qclass_name'
    response_code = models.CharField(max_length=50, null=True, blank=True)  # 'rcode_name'

    rtt = models.FloatField(null=True)  # 'rtt'
    rejected = models.BooleanField(default=False, null=True, blank=True)  # 'rejected'

    AA = models.BooleanField(default=False, null=True, blank=True)  # 'AA'
    TC = models.BooleanField(default=False, null=True, blank=True)  # 'TC'
    RD = models.BooleanField(default=True, null=True, blank=True)  # 'RD'
    RA = models.BooleanField(default=False, null=True, blank=True)  # 'RA'

    name = models.CharField(max_length=255, null=True, blank=True)
    handle = models.CharField(max_length=255, null=True, blank=True)  # CIDR
    start_address = models.CharField(max_length=50, null=True, blank=True)
    end_address = models.CharField(max_length=50, null=True, blank=True)

    created = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True, null=True, blank=True)

    score = models.IntegerField(default=50, null=True, blank=True)

    def __str__(self):
        return self.name

    def parameters(self):
        params = ['id', 'query', 'answer', 'query_type', 'query_class', 'response_code', 'score']
        return params
