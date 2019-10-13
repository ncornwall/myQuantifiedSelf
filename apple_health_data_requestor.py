
    def get_apple_data(self):
        path_to_exportxml = "data/apple_health_export/export.xml"
        e = xml.etree.ElementTree.parse(path_to_exportxml).getroot()
        df = pd.DataFrame(list(iter_records(e)))

    def iter_records(healthdata):
        healthdata_attr = healthdata.attrib
        for rec in healthdata.iterfind('.//Record'):
            rec_dict = healthdata_attr.copy()
            rec_dict.update(healthdata.attrib)
            for k, v in rec.attrib.items():
                if 'date' in k.lower():
                    rec_dict[k] = datetime.datetime.strptime(v, '%Y-%m-%d %H:%M:%S %z')
                else:
                    rec_dict[k] = v
            yield rec_dict

        e = xml.etree.ElementTree.parse(path_to_exportxml).getroot()
        df = pd.DataFrame(list(iter_records(e)))

        df