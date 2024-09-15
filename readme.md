User defined schema in flask
============================

* A simple attempt to define a customizable schema for a flask/ sqlalchemy model.


How it works
------------
* The database stores the entities in the 'der.data' jsonb field
* How does it know it's valid? It uses the latest schema defined in the 'der.schema' table
* The schema there is an AVRO schema; conveniently this too is stored in a jsonb field
* This way, the schema can be changed without changing the code
* If the schema is updated then each der object will need to be revalidated; these can be filtered using the 'validation_schema' field. How and what to do with these is not covered here; it may be a batch job.
* What about data-related validation? if (say) we require that a 'latitude' value must be accompanied by a 'longitude'? In this case we can rely on the rules engine validation
* The rules engine takes rules such as the above - or (say) 'age must be > 18' and also applies these to the data.
 
License
-------
This work is licensed under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

