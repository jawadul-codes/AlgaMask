"""Presentation derived from stored facts; never upgrades source support to recipe proof."""

INGREDIENT_NAMES = {
    'IF-SPI-PWD': 'Spirulina powder', 'IF-CHL-PWD': 'Chlorella powder',
    'IF-OAT-DRY': 'Dry oats', 'IF-DATE-DRIED': 'Dried dates',
    'IF-COCOA-PWD': 'Cocoa powder', 'IF-CINN-PWD': 'Cinnamon powder',
    'IF-VAN-EXT': 'Vanilla extract', 'IF-ORANGE-PEEL': 'Raw orange peel',
}


def evidence_scope(item, request):
    requested = {'spirulina', 'chlorella'} if request.algae.value == 'blend' else {request.algae.value}
    species = set(item.get('species', []))
    matrix = item.get('matrix') or 'not recorded'
    tag = item.get('chunk_tag')
    label = ('Hypothesis or evidence limitation' if item.get('support_class') == 'hypothesis'
             else 'Species background' if tag == 'diagnosis' and requested <= species
             else 'Related-study background')
    notes = [f'Study material: {matrix}.']
    if not species:
        notes.append('Species applicability is unspecified.')
    elif not requested <= species:
        notes.append('The study does not cover all requested algae species.')
    else:
        notes.append('The study includes the requested species; material and supplier may differ.')
    notes.append('Source support describes the cited statement, not validation of this recipe.')
    notes.append('The selected flavour, inclusion and masking effect have not been validated for this recipe.')
    return {'label': label, 'notes': notes, 'recipe_validated': False}


def interpret(result):
    status = result.status
    if status == 'generation_failed':
        title = 'Evidence explanation could not be verified'
        reason = 'No formulation is available because the cited explanation failed its checks.'
    elif status != 'report_ready' or not result.formulations:
        title = 'No candidate returned for this configuration'
        reason = 'No candidate was returned. Review the recorded reasons below before adjusting inputs.'
    elif result.mode == 'mock':
        title = 'Demonstration result — synthetic ingredients and evidence'
        reason = 'This result is a software fixture; it does not establish nutritional or sensory performance.'
    else:
        title = 'Candidates passed computational checks'
        reason = ('Fixed ingredient amounts were checked against the requested targets.' if
                  result.request.experiment == 'spirulina-proof-v1' else
                  'Candidates from nine recipe variations are ordered by estimated protein, then candidate ID.')
    reasons = []
    if status != 'report_ready' or not result.formulations:
        audit = result.impact.get('screening', {})
        if audit.get('reason'):
            reasons.append(audit['reason'])
        for errors in audit.get('verdicts', {}).values():
            reasons.extend(errors)
        for step in result.trace:
            if step.status == 'blocked':
                reasons.append(step.summary)
    sensory = 'Sensory effects and flavour masking are unmeasured. No risk score or improvement percentage is available.'
    if any(isinstance(item.get('relative_risk'), (int, float)) for item in result.sensory_map):
        sensory += ' Historical demo scores in the stored record are illustrative only, not measurements.'
    values = (result.impact.get('nutrition', {}).get(result.formulations[0].id, {}).get('per_serving', {})
              if result.formulations else {})
    unavailable = [label for key, label in [('protein_g', 'protein'), ('energy_kcal', 'energy'), ('sugar_g', 'sugar')]
                   if values.get(key) is None]
    nutrition_notice = ('No candidate nutrition values are available.' if not result.formulations else
                        'Selected candidate has unknown ' + ', '.join(unavailable) + '. Unknown does not mean zero.'
                        if unavailable else 'Selected candidate nutrition values are composition estimates, not product measurements.')
    return {'version': 'report-clarity-v1', 'title': title, 'reason': reason,
            'ingredient_names': INGREDIENT_NAMES,
            'nutrition_notice': nutrition_notice,
            'blocking_reasons': list(dict.fromkeys(reasons)),
            'sensory': sensory,
            'controls': 'B0 and A0 are comparison controls. Nutrition targets apply to candidates only; controls may exceed those limits.',
            'mass_basis': f'Nutrition is estimated per {result.request.serving_g:g} g ingredient input. Finished product yield is unmeasured.',
            'evidence': {e['chunk_id']: evidence_scope(e, result.request) for e in result.evidence}}
