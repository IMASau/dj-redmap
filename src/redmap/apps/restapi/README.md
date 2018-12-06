
The REST API provides the services necessary for mobile applications to provide a specific set of functionality.

Associated database changes:
* update_time fields for sightings





DB CHANGES
====================================
BEGIN;
-- Application: redmapdb
-- Model: Sighting
ALTER TABLE "RM_SIGHTING"
	ADD "update_time" datetime;
COMMIT;
