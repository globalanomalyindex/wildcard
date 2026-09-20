# What failed in the first calibration

This is descriptive inspection after the first calibration, not a new scoring rule or a confirmatory effect test. The complete records and original scores remain unchanged.

The direct programs passed all 2,048 hidden traces. Matched and shuffled outside conditions each passed 1,979/2,048, with all 69 failures in the pin-aware FIFO task `dev-c01`. At the first inspected difference (`dev-c01/ordinary/12`, event 19), a pinned resident was invalidated a second time while already tombstoned. Both outside programs returned status `ignored`; the task requires `invalidated` for a pinned resident and reserves `missing` for an absent key. The resident remained present, pinned and tombstoned in all versions. The reported cache-state fields agreed; the acknowledgement status did not.

This is a real failure of the specified output contract, not evidence of lost data or an unsafe cache. The whole-trace score intentionally fails a trace when any required output differs, so a repeated acknowledgement mistake can affect many traces. It would be misleading to describe the observed percentage as the proportion of data corrupted, or to infer a general harmful effect of outside relations from this eight-task calibration.

The example also shows the gate's limitation. Public consistency and rejection of supplied incorrect outputs do not prove complete coverage of all task rules. The gate is finite evidence, and a final program can still fail unseen combinations. Development-2 was chosen because D reached the predefined ceiling; these outside-arm failures did not select its difficulty revision.
