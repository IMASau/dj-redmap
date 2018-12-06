BEGIN;
CREATE TABLE "surveys_survey" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(255) NOT NULL,
    "slug" varchar(255) NOT NULL,
    "enabled" bool NOT NULL,
    "survey" text NOT NULL
)
;
COMMIT;
