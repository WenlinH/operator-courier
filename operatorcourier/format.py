import yaml
from operatorcourier.build import BuildCmd


DATA_KEY = 'data'
CRD_KEY = 'customResourceDefinitions'
CSV_KEY = 'clusterServiceVersions'
PKG_KEY = 'packages'


class _literal(str):
    pass


def _literal_presenter(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')


def _get_empty_formatted_bundle():
    return {
        DATA_KEY: {
            CRD_KEY: '',
            CSV_KEY: '',
            PKG_KEY: '',
        }
    }


def format_bundle(bundle):
    """
    Converts a bundle object into a push-ready bundle by
    changing list values of 'customResourceDefinitions',
    'clusterServiceVersions', and 'packages' into stringified yaml literals.

    This format is required by the Marketplace backend.

    :param bundle: A bundle object
    """

    formattedBundle = _get_empty_formatted_bundle()

    yaml.add_representer(_literal, _literal_presenter)

    if DATA_KEY not in bundle:
        return formattedBundle

    # Format data fields as string literals to match backend expected format
    if bundle[DATA_KEY].get(CRD_KEY):
        formattedBundle[DATA_KEY][CRD_KEY] = _literal(
            yaml.dump(bundle[DATA_KEY][CRD_KEY],
                      default_flow_style=False))

    if CSV_KEY in bundle[DATA_KEY]:
        # Format description and alm-examples
        clusterServiceVersions = []
        for csv in bundle[DATA_KEY][CSV_KEY]:
            if csv.get('metadata', {}).get('annotations', {}).get('alm-examples'):
                csv['metadata']['annotations']['alm-examples'] = _literal(
                    csv['metadata']['annotations']['alm-examples'])

            if csv.get('spec', {}).get('description'):
                csv['spec']['description'] = _literal(csv['spec']['description'])

            clusterServiceVersions.append(csv)

        if clusterServiceVersions:
            formattedBundle[DATA_KEY][CSV_KEY] = _literal(
                yaml.dump(clusterServiceVersions, default_flow_style=False))

    if bundle[DATA_KEY].get(PKG_KEY):
        formattedBundle[DATA_KEY][PKG_KEY] = _literal(
            yaml.dump(bundle[DATA_KEY][PKG_KEY], default_flow_style=False))

    return formattedBundle


def unformat_bundle(formattedBundle):
    """
    Converts a push-ready bundle into a structured object by changing
    stringified yaml of 'customResourceDefinitions', 'clusterServiceVersions',
    and 'packages' into lists of objects.
    Undoing the format helps simplify bundle validation.

    :param formattedBundle: A push-ready bundle
    """

    bundle = BuildCmd()._get_empty_bundle()

    if DATA_KEY not in formattedBundle:
        return bundle

    if CRD_KEY in formattedBundle[DATA_KEY]:
        crds_list = yaml.safe_load(formattedBundle[DATA_KEY][CRD_KEY])
        if crds_list:
            bundle[DATA_KEY][CRD_KEY] = crds_list

    if CSV_KEY in formattedBundle[DATA_KEY]:
        csvs_list = yaml.safe_load(formattedBundle[DATA_KEY][CSV_KEY])
        if csvs_list:
            bundle[DATA_KEY][CSV_KEY] = csvs_list

    if PKG_KEY in formattedBundle[DATA_KEY]:
        packages_list = yaml.safe_load(formattedBundle[DATA_KEY][PKG_KEY])
        if packages_list:
            bundle[DATA_KEY][PKG_KEY] = packages_list

    return bundle
