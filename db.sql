CREATE TABLE DOCIPDOC (
    ID                  BIGINT,
    ID_DOCNO            VARCHAR(40),
    ID_DOCDATE          DATE,
    DOC_NUMBER          VARCHAR(40),
    IP_RISE_DATR        DATE,
    IP_DATE_FINISH      DATE,
    ID_DBTR_NAME        VARCHAR(1000),
    ID_DEBTSUM          DECIMAL(18,2),
    DOCSTATUSID         INTEGER,
    IP_EXEC_PRIST_NAME  VARCHAR(95),
    ID_CRDR_NAME        VARCHAR(1000),
    ARTICLE             INTEGER,
    POINT               INTEGER,
    SUBPOINT            INTEGER
);

CREATE TABLE FROMFNS (
    PK          BIGINT NOT NULL,
    DEBTR_INN   VARCHAR(12),
    DEBTR_NAME  VARCHAR(1000),
    NUM_ID      VARCHAR(100),
    DATE_ID     DATE,
    SUM_ALL     DECIMAL(15,2),
    NUM_SV      BIGINT,
    OSP         VARCHAR(1000),
    FILENAME    VARCHAR(100)
);




/******************************************************************************/
/***                              Primary Keys                              ***/
/******************************************************************************/

ALTER TABLE FROMFNS ADD CONSTRAINT PK_FROMFNS PRIMARY KEY (PK);
