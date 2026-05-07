CREATE TABLE IF NOT EXISTS youth_policies (
    "plcyNo"            VARCHAR(30)  PRIMARY KEY,
    "plcyNm"            TEXT,
    "plcyExplnCn"       TEXT,
    "plcySprtCn"        TEXT,
    "plcyKywdNm"        TEXT,
    "lclsfNm"           TEXT,
    "mclsfNm"           TEXT,
    "sprtTrgtMinAge"    VARCHAR(5),
    "sprtTrgtMaxAge"    VARCHAR(5),
    "sprtTrgtAgeLmtYn"  VARCHAR(1),
    "bizPrdBgngYmd"     VARCHAR(20),
    "bizPrdEndYmd"      VARCHAR(20),
    "bizPrdEtcCn"       TEXT,
    "aplyUrlAddr"       TEXT,
    "refUrlAddr1"       TEXT,
    "refUrlAddr2"       TEXT,
    "sprvsnInstCdNm"    TEXT,
    "operInstCdNm"      TEXT,
    "plcyAplyMthdCn"    TEXT,
    "mrgSttsCd"         TEXT,
    "earnCndSeCd"       TEXT,
    "earnMinAmt"        TEXT,
    "earnMaxAmt"        TEXT,
    "frstRegDt"         TIMESTAMP,
    "lastMdfcnDt"       TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_youth_policies_region
    ON youth_policies ("sprvsnInstCdNm");

CREATE INDEX IF NOT EXISTS idx_youth_policies_domain
    ON youth_policies ("lclsfNm", "mclsfNm");
