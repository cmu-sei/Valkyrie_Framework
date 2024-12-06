# IP Address Search Using IP Maven

Below are the two options to search for an IP address using the IP Maven Whois API Endpoint.

The endpoints return a list of JSONs of each entry whose IP address matches with your search query.

The only variables in each are the IPTOSEARCH field, which is whatever IP address the user wishes to learn more about.

### /api/whois/?search_query=IPTOSEARCH

This method is simpler but will take longer because it will search on every column for the IPTOSEARCH but in theory, it is redundant to search on a column like 'customer_name' for the IP address.

### <span style="color:red">[RECOMMENDED]</span> /api/whois/?search_by=start_address,end_address&search_query=IPTOSEARCH

This is the recommended method, as the backend is implement such that it will only search for IPTOSEARCH on columns 'start_address' and 'end_address', meaning its execution will be faster.

For example, if I want to learn more about the IP address 173.42.47.71, I would call the endpoint with:

```shell
http://127.0.0.1:8000/api/whois/?search_query=173.42.47
```

or

```shell
http://127.0.0.1:8000/api/whois/?search_by=start_address,end_address&search_query=173.42.47
```