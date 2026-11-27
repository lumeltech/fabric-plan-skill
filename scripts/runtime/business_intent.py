"""Route an agent's semantic interpretation, not literal prompt keywords.

This local planner does not infer financial assumptions or create artifacts.
The agent translates the user's words into business outcomes and records evidence;
the planner preserves every outcome, dependencies and unresolved decisions.
"""
import copy
from .discovery import catalog

ROUTES={
 'shared-assumption':(['F20','F05'],['anchor-construct'],['measure','sheetGrain','rowDimensions','columnDimensions','eligibleScope','aggregation','distribution','consumers','displayAtAllLevels']),
 'display-anchor':(['F20','F12'],['anchor-construct'],['measure','sheetGrain','rowDimensions','columnDimensions','consumers','displayAtAllLevels']),
 'time-intelligence':(['TIME-INTELLIGENCE','FORMULAS'],['planning-time-column','formula'],['source','period','cutoffScope','cutoffControl','cutoff','aggregation','missingPolicy']),
 'one-time-column':(['TIME-INTELLIGENCE','F05'],['input','formula'],['kind','grain','placement','storageContext']),
 'editable-value':(['F05'],['input'],['unit','grain','default']),
 'conditional-input':(['F30'],['input','forecast'],['target','condition','expression','scope']),
 'calculated-value':(['FORMULAS','F02'],['formula'],['expression','inputs','aggregation']),
 'rolling-forecast':(['F09','TIME-INTELLIGENCE'],['forecast'],['actuals','grain','openPeriod','openDefault','timezone']),
 'balance-roll-forward':(['ROLL-FORWARD','FORMULAS','F09','F12','F01'],['roll-forward-presentation','planning-totals','formula'],['grain','calendar','unit','seedAuthority','movements','signConvention','forecastCutoff','editableFields','dependencyStrategy','aggregation']),
 'reuse-values':(['F19'],['resolve-measure-binding'],['sourceOrigin','source','targetGrain','transformation','grainCompatibility']),
 'commentary':(['F05','TIME-INTELLIGENCE'],['input'],['grain','placement']),
 'comparison':(['F15'],['resolve-measure-binding'],['current','baseline','grain','difference','favorableDirection','unit']),
 'conditional-format':(['CONDITIONAL-FORMATTING','F15'],['build','format-matrix'],['target','condition','meaning']),
 'storage-identity':(['DIMENSION-ID'],['leaf-key-mapping','mapping'],['leaf','idField','ancestorDependency']),
 'master-data-maintenance':(['POWERTABLE'],['powertable','table-source'],['source','key','editableColumns']),
 'allocation':(['RULES'],['rule'],['source','targetGrain','weights','missingWeights','totalRule']),
 'approval':(['F13'],[],['scope','stages']),
 'access-control':(['F25'],[],['scope','audience','policy']),
 'scenario':(['SCENARIOS'],['input','filters','build'],['behavior','scope']),
 'navigation':([],[],['destinations'])
}

def plan_intent(brief):
    if not isinstance(brief.get('request'),str) or not brief['request'].strip():raise ValueError('Retain the complete business request')
    reqs=brief.get('requirements')
    if not isinstance(reqs,list) or not reqs:raise ValueError('Agent must decompose the request into business outcomes')
    ids=[r.get('id') for r in reqs]
    if any(not isinstance(i,str) or not i for i in ids) or len(ids)!=len(set(ids)):raise ValueError('Unique requirement IDs required')
    data=catalog();modules={m['id']:m for m in data['modules']};results=[];graph={}
    for r in reqs:
        if not r.get('text'):raise ValueError('Retain the original business clause for '+r['id'])
        kind=r.get('intent');details=r.get('details',{});depends=r.get('dependsOn',[])
        if not isinstance(details,dict) or not isinstance(depends,list):raise ValueError('Invalid structured intent')
        if set(depends)-set(ids):raise ValueError('Unknown dependency for '+r['id'])
        graph[r['id']]=depends;needs=[];notes=[]
        if kind not in ROUTES:
            mids=[];ops=[];needs=['Resolve this outcome through the full module directory; no matching intent shortcut']
        else:
            mids,ops,required=copy.deepcopy(ROUTES[kind])
            needs=[k for k in required if k not in details or details[k] is None or details[k]=='']
        if kind=='reuse-values':
            origin=details.get('sourceOrigin');transform=details.get('transformation');grain=details.get('grainCompatibility')
            if origin=='semantic' and transform=='direct':
                mids=['F21'];ops=['resolve-measure-binding'];notes.append('Reuse the original PowerBI assignment, not its Native Planning companion as From Sheets.')
            elif transform in ('join','merge','append','sql','aggregate'):
                mids=['F18'];ops=['bridge-source','bridge-'+('construct-query' if transform=='aggregate' else transform),'bridge-consumer']
                notes.append('Resolve transformed query outputs before assigning InfoBridge IDs. A saved graph does not prove refresh or materialization.')
            elif origin=='query' and transform=='direct':
                mids=['F18'];ops=['bridge-consumer','resolve-measure-binding']
            elif origin=='sheet' and transform=='direct' and grain in ('same','coarser-compatible'):
                notes.append('Link the produced input/Forecast/formula output at its resolved source ID; do not duplicate inputs.')
            elif origin and transform:
                needs.append('Resolve supported source/transformation/grain combination before linking')
        if kind in ('shared-assumption','display-anchor'):
            if modules['F20'].get('authoringEnabled') is False:
                ops=[]
                needs.append('Anchor authoring is disabled by the selected package policy; guidance and examples remain available')
            notes.append('Anchor at the independent business decision grain; omitted axes mean All/Total. Retain formula/native calculation and input identity. Hide repeated instances with display_at_all_levels=false, not visible=false or deleted data.')
            notes.append('Leaf formulas retain applicable underlying values via existing calculation/distribution. Visibility, edit permission and allocation are separate; anchors do not supply a dynamic lookup or time intelligence.')
            notes.append('Expose the exact Year/Quarter/All entry intersection. Column-subtotal-off has a scoped exception for an intermediate anchor entry; ordinary report defaults remain.')
            if details.get('rowDimensions') == [] and details.get('columnDimensions') == []:
                needs.append('At least one selected row or column dimension is required')
            notes.append('The builder computes the native XXH3 hash from all ordered current pivot dimensions, including the first anchor. Resolve exact source metadata IDs before construction.')
            if kind=='shared-assumption' and details.get('valueSemantics')=='amount-pool' and details.get('distribution')=='copy':
                needs.append('An amount pool needs allocation; do not copy the whole pool to each leaf')
        if kind=='balance-roll-forward':
            notes.append('Read the complete matched worked case and shared formula patterns. Resolve first-visible seed, prior-cohort lookback, zero/blank and prefill policies; do not infer dates or source tables from examples.')
            notes.append('Recommend Measures in Rows with a logical native measure_tree: opening, movement drivers, closing, diagnostics. Hierarchy is presentation; preserve formula arithmetic, per-axis aggregation and source/storage identities.')
            notes.append('Backward temporal recurrence is distinct from a same-period cycle. Cumulative ranges require independent additive movements; balance-driven attrition/caps need recurrence or a supported sequential process. The generic build dependency guard does not accept a cyclic measure graph.')
        if kind in ('time-intelligence','one-time-column'):
            notes.append('Preserve the primary time hierarchy. Append a Visual Input or Formula Visual Column once per row context; distinguish presentation from persistence grain.')
        if kind=='time-intelligence':
            notes.append('Evaluate Intelligence slicer -> DAX SELECTEDVALUE -> exposed Planning measure first for shared cutoff control. Use a sheet parameter for local scope or a documented unsuitable dashboard route. Preserve required history and resolve year/month ambiguity.')
            if details.get('cutoffScope')=='dashboard' and details.get('cutoffControl')=='parameter' and not details.get('dashboardRouteUnsuitableReason'):
                needs.append('Resolve shared dashboard slicer route or explain why it is unsuitable')
        if kind=='rolling-forecast':
            notes.append('Prefer separate Year/Quarter/Month fields and only valid calendar attributes in Forecast Columns; weekly parentage and deliberate composite exceptions require evidence.')
            notes.append('If the result is a balance carried between periods, also decompose a balance-roll-forward outcome; extending a forecast horizon alone is not a balance bridge.')
            notes.append('Native Forecast is appropriate for actuals-controlled closed periods plus editable open periods; dates, growth formula and time grain are request-specific.')
        if kind in ('editable-value','rolling-forecast','commentary'):
            notes.append('New editable inputs default explicitly to ReadAndEdit. Route business lock/unlock conditions to F30 with a real BasedOnFormula expression; preserve existing locks on scoped repairs.')
        if kind=='conditional-input':
            notes.append('Write a positive Boolean eligibility expression using current source identities in allow_input.BasedOnFormula; this is separate from defaults, on-change actions, Forecast closure and access permissions.')
        if kind=='conditional-format':
            notes.append('For new reports use sheet.conditionalFormatting with stable measure keys; standard construction emits the current UI-derived numeric profile in both stores. For repairs resolve the current owner and preserve unrelated rules. Saved rule counts do not establish UI recognition.')
        if kind=='comparison':
            notes.append('Integrated variance is the default bar/column comparison. Keep units/grain compatible, real AC/PY sources and the declared favorable direction.')
        if kind=='commentary':
            notes.append('Choose a text measure repeated at period grain or an outside-axis visual column from the business placement; do not infer from the word note alone.')
        if kind=='allocation':
            notes.append('Weighted allocation is separate from the numeric distribute-parent-to-children toggle.')
        if kind=='scenario':
            notes.append('Distinguish a transient sensitivity input, persisted version Context and native scenario lifecycle; the basic constructors do not cover all three.')
            if details.get('behavior') not in ('transient-sensitivity','persisted-version-context'):
                needs.append('Resolve native scenario lifecycle or ambiguous scenario behavior; the selected constructors do not implement it')
        if kind=='navigation':
            needs.append('Navigation publication is not provided by the supported planner routes')
        if kind in ('approval','access-control'):
            needs.append('Selected package has guide-only coverage; resolve a supported implementation without substituting slicers or colors for controls')
        guides=[]
        for mid in mids:
            for g in modules[mid]['guides']:
                if g not in guides:guides.append(copy.deepcopy(g))
        results.append({'id':r['id'],'text':r['text'],'intent':kind,'details':details,'dependsOn':depends,'modules':mids,
          'evidence':copy.deepcopy(r.get('evidence',[])),
          'guides':guides,'operations':[{'id':op,**copy.deepcopy(data['actions'][op])} for op in ops],
          'status':'needs-resolution' if needs else 'route-selected','unresolved':needs,'decisions':notes,
          'execution':'not-started'})
    order=[];seen=set();active=set()
    def walk(key):
        if key in active:raise ValueError('Business dependency cycle: '+key)
        if key in seen:return
        active.add(key)
        for dep in graph[key]:walk(dep)
        active.remove(key);seen.add(key);order.append(key)
    for key in ids:walk(key)
    return {'request':brief['request'],'requirements':results,'executionOrder':order,
      'defaultPolicy':{'source':'planning-presentation.md','nonNegotiable':True,'completionGate':'runtime.application_defaults.require_delivery_phases',
        'scope':'Public definition only; role-specific Home content and priority are not published.',
        'required':['Arial for all authored text','Home visibility enabled in the public definition','rich sheet header and source-role legend','source-role measure colors','Intelligence header/slicers/charts/owner-preserving embed','canonical source names and typed identities','complete formatting and dynamic column presentation','stable leaf-key storage where dependency is established','integrated variance for baseline comparison bars','visible assigned measure cards at All without preset restrictions','per-measure Auto number scaling for numeric Planning measures']},
      'presentationDefaults':{'totals_config':{'row_grand_total':'Top','row_sub_total':'Top','column_grand_total':'Left','column_sub_total':None},'measureBasedRollForward':'Recommend Measures in Rows with a logical native Measure Model; preserve explicit user choices'},
      'businessAssumptions':copy.deepcopy(brief.get('assumptions',[])),
      'noImplicitBusinessConstants':['2026 dates','10 percent growth','15 percent merit limit','3 percent inflation','monthly time grain','USD currency','particular table or field names'],
      'recipePolicy':'Reuse a whole case only if business semantics match; otherwise compose relevant patterns and explicit parameter changes.',
      'readyForAuthoring':all(not r['unresolved'] for r in results),'runtimeValidation':'not run',
      'completion':'Routing and prerequisite ledger only. Resolve fields and execute every requested supported phase before claiming delivery.'}
