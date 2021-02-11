/*

* Version:          0.1

* Revision date:    10-09-2020

* Author:           Daniel Beernink

*

* Platform:         CTT2.0 Modality

* Type:             Specific Query

* Description:      This query differentiates moves in two types of moves: internal moves from location to locaton and other moves for the terminal CTT Rotterdam

*

* Checked by:

*/

--

SELECT

    t.SEQ,

    TO_DATE(DECODE(t.INSDATE, NULL, NULL, TO_CHAR(TO_DATE(TO_CHAR(t.INSDATE, 'DD-MM-YYYY') || ' ' || LPAD(t.INSTIME, 4, '0'), 'DD-MM-YY HH24MI'), 'DD-MM-YYYY HH24:MI:SS')),'DD-MM-YYYY HH24:MI:SS') AS movedate,

    t.COMPOUNDPOS_FROM,

    t.COMPOUNDPOS_TO,

    t2.UNITNR,

    t2.ADDRESS_OWNLOC AS location,

    t2.SEQ,

    t2.UNITTYPE,

    t2.ADDRESS_CLIENT,

    (CASE

      WHEN

            t.COMPOUNDPOS_FROM LIKE '%.%.%'

            AND t.COMPOUNDPOS_TO LIKE '%.%.%'

            THEN 'InternalMoveLocations'

      WHEN t.COMPOUNDPOS_FROM LIKE '%.%.%'

            AND t.COMPOUNDPOS_TO = 'BIJGEREDEN'

            THEN 'InternalMoveLocations'

      WHEN t.COMPOUNDPOS_FROM = 'TERM'

            AND t.COMPOUNDPOS_TO LIKE '%.%.%'

            THEN 'InternalMoveLocations'

      WHEN t.COMPOUNDPOS_FROM = NULL

            AND t.COMPOUNDPOS_TO = 'TOUT'

            THEN 'Responsible fout'

      WHEN t.COMPOUNDPOS_FROM = 'TOUT'

            AND t.COMPOUNDPOS_TO = NULL

            THEN 'Responsible fout'

      WHEN t.COMPOUNDPOS_FROM = 'TIN'

            AND t.COMPOUNDPOS_TO LIKE '%.%.%'

            THEN 'Gate in train'

      WHEN t.COMPOUNDPOS_FROM LIKE '%.%.%'

            AND t.COMPOUNDPOS_TO = 'TOUT'

            THEN 'Gate out train'

      WHEN t.COMPOUNDPOS_FROM = 'TRUCK'

            AND t.COMPOUNDPOS_TO LIKE '%.%.%'

            THEN 'Gate in truck'

      WHEN t.COMPOUNDPOS_FROM LIKE '%.%.%'

            AND t.COMPOUNDPOS_TO = 'TRUCK'

            THEN 'Gate out truck'

      WHEN t.COMPOUNDPOS_FROM = 'BIN'

            AND t.COMPOUNDPOS_TO LIKE ('%.%.%')

            THEN 'Gate in barge'

      WHEN t.COMPOUNDPOS_FROM LIKE '%.%.%'

            AND t.COMPOUNDPOS_TO = 'BOUT'

            THEN 'Gate out barge'

      WHEN t.COMPOUNDPOS_FROM = 'BIJGEREDEN'

            AND T.COMPOUNDPOS_TO = 'BOUT'

            THEN 'Gate out barge'

      WHEN t.COMPOUNDPOS_FROM = 'TERM'

            AND t.COMPOUNDPOS_TO = 'BIJGEREDEN'

            THEN 'InternalMoveLocations'

      WHEN t.COMPOUNDPOS_FROM = 'VERWARMEN'

            AND T.COMPOUNDPOS_TO LIKE '%.%.%'

            THEN 'InternalMoveLocations'

      WHEN t.COMPOUNDPOS_FROM LIKE '%.%.%'

            AND t.COMPOUNDPOS_TO = 'VERWARMEN'

            THEN 'InternalMoveLocations'

      WHEN t.COMPOUNDPOS_FROM = 'BURGERHEK'

            AND t.COMPOUNDPOS_TO LIKE '%.%.%'

            THEN 'InternalMoveLocations'

      WHEN t.COMPOUNDPOS_FROM LIKE '%.%.%'

            AND t.COMPOUNDPOS_TO = 'BURGERHEK'

            THEN 'InternalMoveLocations'

      WHEN t.COMPOUNDPOS_FROM = 'BIN'

            AND t.COMPOUNDPOS_TO = 'TERM'

            THEN 'Gate in barge'

      WHEN t.COMPOUNDPOS_FROM = 'TIN'

            AND t.COMPOUNDPOS_TO = 'TERM'

            THEN 'Gate in train'

      ELSE 'Rotzooi'

      END) AS MOVETYPE

FROM

    CTT2.TERMMOVE t

LEFT JOIN CTT2.TERM t2 ON

    t2.SEQ =t.TERM

LEFT JOIN CTT2.VOYTERM vin ON

    t2.VOYTERM_IN = vin.CODE

LEFT JOIN CTT2.VOYTERM vout ON

    t2.VOYTERM_OUT = vout.CODE

LEFT JOIN CTT2.BARGE b ON

    vin.BARGE = b.CODE

LEFT JOIN CTT2.BARGE b2 ON

    vout.BARGE = b2.CODE

WHERE

    t.INSDATE >= SYSDATE -7

    AND (t.COMPOUNDPOS_FROM NOT IN ('LSC') OR t.COMPOUNDPOS_TO NOT IN ('LSC'))

    AND t2.ADDRESS_OWNLOC = 'CTTROT'

ORDER BY UNITNR, MOVEDATE
