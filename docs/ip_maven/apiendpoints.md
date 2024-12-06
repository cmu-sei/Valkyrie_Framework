# IP Maven API Endpoints

## Whois Endpoints

1. **api/whois**

    List entire database of IP address data. Equivalent to <span style="color:gray">api/whois/?page_number=1&page_size=100</span>.

2. **api/whois/?search_query=keyword**

    Search every column of the Whois database for the keyword.

    Example 1: <span style="color:gray"> api/whois/?search_query=carnegie</span> searches for entries that contain 'carnegie' in any column.

3. **api/whois/?search_by=parameter&search_query=keyword**

    Search the 'parameter' column of the Whois database for the keyword. If 'parameter' is not a valid search term, cause 400.

    Example 1: <span style="color:gray"> api/whois/?search_by=name&search_query=carnegie</span> searches for entries that contain 'carnegie' in the column 'name'.

    Example 2 <span style="color:red">(Error)</span>: <span style="color:gray"> api/whois/?search_by=water&search_query=carnegie</span> will error because 'water' is not a valid column in the Whois database.

4. **api/whois/?search_by=parameter1,parameter2,...,parameterN search_query=keyword**

    Search on all parameter columns for the keyword. If any parameter is not a valid search term, cause 400.
    
    Example 1: <span style="color:gray"> api/whois/?search_by=name,customer_name&search_query=carnegie</span> searches for entries that contain 'carnegie' in either the column 'name' or 'customer_name'.

5. **api/whois/?search_by=parameter1,parameter2,...,parameterN&search_query=keyword1,keyword2,...,keywordN&require_all=requires_value**

    Search for keywordX on parameterX for all X from 1 to N. Number of parameters and keywords must match.If any parameter is not a valid search term, cause 400.

    * **requires_all** parameter in the URL can be true or false. If not provided, defaults to false.
        * If true, then only select rows satisfying every parameter, keyword pair
        * If false, then select all rows that satisfy at least one of the parameter,keyword pairs

    Example 1: <span style="color:gray"> api/whois/?search_by=customer_name,start_address&search_query=carnegie,40.132</span> searches for entries where 'customer_name' contains 'carnegie' **or** 'start_address' contains '40.132'.

    Example 2: <span style="color:gray"> api/whois/?search_by=customer_name,start_address&search_query=carnegie,40.132&requires_all=True</span> searches for entries where 'customer_name' contains 'carnegie' **and** 'start_address' contains '40.132'.

    Example 3 <span style="color:red">(Error)</span>: <span style="color:gray">api/whois/?search_by=customer_name,start_address,postal_code&search_query=carnegie,40.132</span> will error because the number of search by parameters and search query keywords are different.


## Mappings Endpoints
1. **api/mappings**

    List entire database of IP address data. Equivalent to <span style="color:gray">api/mappings/?page_number=1&page_size=100</span>.

2. **api/mappings/?search_query=keyword**

    Search every column of the Mappings database for the keyword.

3. **api/mappings/?search_by=parameter&search_query=keyword**

    Search the 'parameter' column of the Mappings database for the keyword. If 'parameter' is not a valid search term, cause 400.

4. **api/mappings/?search_by=parameter1,parameter2,...,parameterN&search_query=keyword**

    Search all parameter columns for the keyword. If any parameter is not a valid search term, cause 400.

5. **api/mappings/?search_by=parameter1,parameter2,...,parameterN&search_query=keyword1,keyword2,...,keywordN**

    Search for keywordX on parameterX for all X from 1 to N. Number of parameters and keywords must match.If any parameter is not a valid search term, return 400 response.
