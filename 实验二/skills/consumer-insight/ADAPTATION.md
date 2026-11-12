# Adaptation record

Original GitHub Skill: [funewa/amazon-consumer-insight](https://github.com/funewa/amazon-consumer-insight), path `SKILL.md`.

Adaptation in this project: the published Skill text is retained; project code supplies Bluetooth-earbud CSV/JSON inputs, local evidence IDs, and output paths. No new business Skill definition or semantic rule was added.

Source SHA-256: DD66909E27A95BF4BE65E3006DD1F626808D5DB41869D13C328D82478A623322


The local `src/consumer_insight_adapter.py` is an integration adapter only. It maps the course CSV to the published output contract, uses a small course-vocabulary mapping for deterministic evidence checks, leaves unmatched labels as `unknown`, does not rewrite the published Skill body, and does not call the paid ARI API.
