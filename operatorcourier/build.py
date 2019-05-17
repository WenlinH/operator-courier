import yaml
import operatorcourier.identify as identify


class BuildCmd:
    def _get_empty_bundle(self):
        return dict(
            data=dict(
                customResourceDefinitions=[],
                clusterServiceVersions=[],
                packages=[],
            )
        )

    def _get_field_entry(self, yaml_content):
        yaml_type = identify.get_operator_artifact_type(yaml_content)
        return yaml_type[0:1].lower() + yaml_type[1:] + 's'

    def _update_bundle(self, operator_bundle, manifest_file_info):
        field_entry_key = self._get_field_entry(manifest_file_info[1])
        field_entry = operator_bundle["data"][field_entry_key]

        field_entry.append((manifest_file_info[0], yaml.safe_load(manifest_file_info[1])))
        return operator_bundle

    def build_bundle(self, manifest_files_info_list):
        """build_bundle takes an array of yaml files and generates a 'bundle'
        with those yaml files generated in the bundle format.

        :param manifest_files_info_list: Array of yaml strings to bundle
        """
        bundle = self._get_empty_bundle()
        for manifest_file_info in manifest_files_info_list:
            bundle = self._update_bundle(bundle, manifest_file_info)

        return bundle
