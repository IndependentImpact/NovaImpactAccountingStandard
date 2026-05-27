#### Measurement instruments

##### General

1. Core properties of a good measurement instrument
1. Accuracy (closeness to the true value)
   Does the instrument measure the correct value?
   Requires calibration against a known standard.

👉 Example:
A thermometer that consistently reads +2°C too high is inaccurate.

2. Precision (repeatability)
   If you measure the same thing multiple times, do you get the same result?

👉 Example:
A scale that always gives the same reading (even if slightly wrong) is precise but not necessarily accurate.

3. Resolution (granularity)
   What is the smallest change the instrument can detect?

👉 Example:
A ruler with millimetre markings vs. one with centimetre markings.

4. Sensitivity (responsiveness to change)
   How much does the output change for a given change in the measured quantity?

👉 Example:
A high-quality air quality sensor detects small pollutant changes; a poor one only reacts to large spikes.

5. Range (operating bounds)
   Over what interval can the instrument measure reliably?

👉 Example:
A thermometer designed for 0–50°C is useless in industrial furnaces.

6. Stability / Drift
   Does the instrument maintain its performance over time?

👉 Example:
Sensors that slowly drift out of calibration produce misleading long-term trends.

7. Calibration requirements
   How often does it need calibration, and how easy is that?

👉 Instruments that require constant recalibration are harder to trust operationally.

8. Selectivity (specificity at the instrument level)
   Does it measure only the intended variable, or is it influenced by others?

👉 Example:
A CO₂ sensor that is affected by humidity has low selectivity.

9. Noise / Signal-to-noise ratio
   How much random variation is there in the measurement?

👉 High noise → hard to distinguish real changes from randomness.

10. Response time
    How quickly does the instrument react to changes?

👉 Example:
A slow thermometer lags behind real temperature changes.

11. Robustness / environmental tolerance
    Does it perform well under real-world conditions (temperature, humidity, vibration, etc.)?

👉 Lab-grade instruments often fail in field conditions.

12. Reliability (operational uptime)
    Does it consistently function without failure?

👉 Frequent breakdowns undermine trust, regardless of accuracy.

13. Usability / human factors
    Is it easy to use correctly?

👉 Complex instruments introduce operator error.

14. Traceability (to standards)
    Can measurements be linked back to recognized standards?

👉 Critical for:
Scientific credibility
Regulatory compliance

Note 1: Key distinctions that often get confused

a. Accuracy vs Precision
Accurate but not precise → scattered around the true value
Precise but not accurate → tightly clustered, but wrong
👉 You ideally want both.

b. Sensitivity vs Resolution
Resolution = smallest detectable step
Sensitivity = how strongly output responds
You can have fine resolution but low sensitivity (or vice versa).

Note 2: The meta-insight (again, alignment across layers)

An instrument can be "perfect" in engineering terms and still useless in practice:

Great instrument + bad indicator → measuring the wrong thing precisely
Great instrument + bad methodology → systematic misinterpretation

Example:

A highly accurate satellite sensor measuring vegetation →
still useless for carbon crediting if the methodology ignores permanence.

Practical evaluation checklist
When assessing an instrument, ask:
What is the true quantity being measured?
What are the known sources of error?
How does it behave over time (drift)?
What environmental factors affect it?
How is it calibrated and validated?
What level of precision/accuracy is actually needed? (often overlooked)
What failure modes exist—and how detectable are they?

##### Questionnaires

Assessing a questionnaire as a measurement instrument:

(TODO: CJP says there's a whole discipline for this - something like "psychometric methods.")

1. Accuracy → Construct validity (are you measuring the right thing?)
   Do the items actually capture the underlying concept (e.g., "health", "well-being", "risk awareness")?
   Evidence:
   Content validity (expert review, coverage of the construct)
   Convergent validity (correlates with other measures of the same construct)
   Discriminant validity (does not correlate with unrelated constructs)
   Red flags: vague wording, items that tap multiple concepts ("double-barrelled"), or heavy dependence on respondents' interpretation.

2. Precision / Noise → Reliability (are responses consistent?)
   If the same person answered again under similar conditions, would you get similar results?
   Common checks:
   Internal consistency (e.g., Cronbach's α / ω)
   Test–retest reliability (stability over time)
   Inter-rater reliability (if ratings involve observers)
   Red flags: items that don't "hang together", large random swings, ambiguous wording.

3. Resolution → Scale granularity
   Can the questionnaire distinguish meaningful differences between respondents?
   Design levers:
   Number of response options (e.g., 5–7 point Likert often works well)
   Clear anchors (what does "4" vs "5" mean?)
   Red flags: too coarse (can't detect change) or too fine (respondents can't reliably differentiate).

4. Sensitivity → Responsiveness to change
   Can it detect real changes when the underlying condition changes?
   How to test:
   Pre/post intervention studies
   Known-groups comparisons (e.g., healthy vs. ill populations)
   Red flags: scores don't move when reality clearly does.

5. Range → Floor & ceiling effects
   Does the scale cover the full spectrum of the construct?
   Check: Are many respondents clustered at the top or bottom?
   Red flags: everyone scores "high" → you can't detect improvement.

6. Selectivity → Bias & confounding control
   Are responses influenced by irrelevant factors?
   Common biases:

- Social desirability ("I answer what looks good")
- Acquiescence (tendency to agree)
- Question order effects
- Cultural/linguistic interpretation
  Mitigations:
- Reverse-coded items
- Neutral wording
- Randomization of item order

7. Stability / Drift → Temporal stability of the instrument
   Does the questionnaire behave the same over time?
   Concerns:

- Changing interpretations of items
- Cultural drift
- Learning effects (respondents "figure out" the test)
  Especially relevant for long-term monitoring.

8. Calibration → Anchoring to external standards
   Can you interpret scores meaningfully?
   Examples:

- Normed scores (population benchmarks)
- Cut-offs (e.g., clinical thresholds)
  Without calibration, a score like "72" is meaningless.

9. Signal-to-noise → Clarity vs respondent burden
   Are you capturing signal, or mostly noise?
   Drivers of noise:

- Long, fatiguing surveys
- Poorly worded items
- Irrelevant questions
  Shorter, well-targeted instruments often outperform long ones.

10. Response time → Practical usability
    How long does it take to complete?
    Does it fit into real workflows?
    If it's too long or intrusive, data quality drops.

11. Robustness → Performance across contexts
    Does it work across:

- Languages
- Cultures
- Modes (online vs in-person)
  Check: Measurement invariance testing (if you want to be rigorous)

12. Usability → Human factors
    Is it easy to understand and complete correctly?
    Check:

- Cognitive interviews ("what did you think this question meant?")
- Pilot testing

13. Traceability → Documentation & provenance
    Do you know:

- Who designed it?
- What assumptions it encodes?
- How it was validated?
  👉 Critical in ESG / audit contexts.

#### Intervention instruments

Efficiency
Effectiveness
Durability
Ease of use
