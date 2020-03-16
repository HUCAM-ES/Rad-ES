import random, datetime, time, json, decimal, re, git, AngioGet
from numpy import around, mean, median, std
from dose_app.models import ModelRequestName, ModelRequestUIDs, ModelRequestDateFixed, ModelRequestDatePeriod
from dose_app.models import ModelPatient, ModelStudyXA, ModelDeletedUID

def angio_get_rand(param_patient_name, param_assoc_IP, param_port, param_calling_aet, param_called_aet = 'server-dicom',
                   param_modality = 'SR'):

    patient_struct = {
        'patient_name': param_patient_name,
        'patient_dob': 0,
        'patient_sex': random.choice(['M', 'F']),

        'study_date': 0,

        'dose_PKA_total': random.random()*100,
        'dose_KAPR_total': random.random()*100,

        'fluoro_PKA_total': random.random()*100,
        'fluoro_KAPR_total': random.random()*100,

        'acq_PKA_total': random.random()*100,
        'acq_KAPR_total': random.random()*100,

        'other': []
    }
    month = random.randint(1, 12)
    day = random.randint(1, 30)
    patient_struct['patient_dob'] = '2018'+(str(month) if month >= 10 else '0'+str(month))+(
                                    str(day) if day >= 10 else '0'+str(day))

    month_study = random.randint(1, 12)
    day_study = random.randint(1, 30)
    patient_struct['study_date'] = '2018' + (str(month_study) if month_study >= 10 else '0' + str(month_study)) + (
                                    str(day_study) if day_study >= 10 else '0' + str(day_study))

    return [patient_struct]


def convert_date(date):
    year = date[0:4]
    month = date[4:6]
    day = date[6:]
    date_correct = datetime.date(int(year), int(month), int(day))
    return date_correct


def convert_date_dash(date):
    year = date[0:4]
    month = date[5:7]
    day = date[8:10]
    date_correct = datetime.date(int(year), int(month), int(day))
    return date_correct


def convert_time(time):
    hour = time[0:2]
    minute = time[2:4]
    second = time[4:6]
    time_correct = datetime.time(int(hour), int(minute), int(second))
    return time_correct


def switch_special(var):
    switcher_dict = {
        'Á': 'A',
        'á': 'a',
        'É': 'E',
        'é': 'e',
        'Í': 'I',
        'í': 'i',
        'Ó': 'O',
        'ó': 'o',
        'Ú': 'U',
        'ú': 'u',
        'À': 'A',
        'à': 'a',
        'È': 'E',
        'è': 'e',
        'Ì': 'I',
        'ì': 'i',
        'Ò': 'O',
        'ò': 'o',
        'Ù': 'U',
        'ù': 'u',
        'Ã': 'A',
        'ã': 'a',
        'Â': 'A',
        'â': 'a',
        'Ê': 'E',
        'ê': 'e',
        'Ô': 'O',
        'ô': 'o',
        'Ç': 'C',
        'ç': 'c',
        '^': '-',
    }
    try:
        return switcher_dict[var]
    except:
        return var


def fix_name_string(string):
    new_str = ""
    for i in string:
        i = switch_special(i)
        i = i.upper()
        new_str = new_str + i
    return new_str


def fix_name_string_URL(string):
    new_str = ""
    for i in string:
        i = switch_special(i)
        i = i.upper()
        new_str = new_str + i
    #new_str = [''.join(i for i in new_str if (i.isalnum() or i=='-' or i=='_'))]
    new_str = re.sub(r'[^a-zA-Z0-9_-]', r'', new_str)
    return new_str


def sum_total(queryset):

    total_dict = {
        'ftt': 0,
        'att': 0,
        'fat': 0,
        'frt': 0,
        'aat': 0,
        'art': 0,
        'dat': 0,
        'drt': 0,
    }
    for patient_study in queryset:
        total_dict['ftt'] += patient_study.fluoro_time_total
        total_dict['att'] += patient_study.acq_time_total
        total_dict['fat'] += patient_study.fluoro_PKA_total
        total_dict['frt'] += patient_study.fluoro_KAPR_total
        total_dict['aat'] += patient_study.acq_PKA_total
        total_dict['art'] += patient_study.acq_KAPR_total
        total_dict['dat'] += patient_study.dose_PKA_total
        total_dict['drt'] += patient_study.dose_KAPR_total

    return total_dict


def statistic_studies(queryset):
    dose_PKA_month = [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00]
    dose_KAPR_month = [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00]
    study_month = [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00]
    patient_month = [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00]
    patient_vec = [[], [], [], [], [], [], [], [], [], [], [], []]
    for patient_study in queryset:

        dose_PKA_month[patient_study.study_date_parsed.month-1] += round(float(patient_study.dose_PKA_total), 2)
        dose_KAPR_month[patient_study.study_date_parsed.month-1] += round(float(patient_study.dose_KAPR_total), 2)
        study_month[patient_study.study_date_parsed.month-1] += 1
        if patient_study.patient.id not in patient_vec[patient_study.study_date_parsed.month-1]:
            patient_month[patient_study.study_date_parsed.month-1] += 1
            patient_vec[patient_study.study_date_parsed.month-1].append(patient_study.patient.id)

    for i in range(len(study_month)):
        if study_month[i] != 0:
            dose_PKA_month[i] = dose_PKA_month[i] / study_month[i]
            dose_KAPR_month[i] = dose_KAPR_month[i] / study_month[i]

    dose_PKA_month = around(dose_PKA_month, 2)
    dose_KAPR_month = around(dose_KAPR_month, 2)

    return dose_PKA_month.tolist(), dose_KAPR_month.tolist(), patient_month, study_month


def create_models_by_name(name_string):
    # True = Query; False = pass
    query_or_pass = False

    while len(name_string) > 0:
        if len(name_string) > 40:
            name_string_block = name_string[:40]
            name_string = name_string[40:]
        else:
            name_string_block = name_string
            name_string = []

        uid_study_vector = AngioGet.study_get(name_string_block, '10.5.136.10', 4096, "projetoDoses", 'server-dicom', 'SR')

        # Obtem UID ainda nao presentes no banco de dados proprio (pedindo para servidor DICOM)
        uid_needed = []
        lista = ModelStudyXA.objects.all().values('uid').filter(uid__in=uid_study_vector)
        uid_current_list = [uid['uid'] for uid in lista]
        for uid in uid_study_vector:
            if uid not in uid_current_list:
                uid_needed.append(uid)
                query_or_pass = True

        # Se UID ainda nao presente em banco, obtem de servidor DICOM
        if query_or_pass:

            angio_study_vector = AngioGet.angio_get_by_uid(uid_needed, '10.5.136.10', 4096, "projetoDoses",
                                                           'server-dicom', 'SR')
            # Se obtem informaçao de Dose, adiciona em banco de dados
            if len(angio_study_vector) >= 1:

                for i in range(len(angio_study_vector)):
                    # Adicona underline em nome para adiçao em URL
                    name_string_URL = angio_study_vector[i]['patient_name'].replace(' ', '_')

                    # Cria paciente
                    patient_model, created = ModelPatient.objects.get_or_create(
                        name=angio_study_vector[i]['patient_name'],
                        name_for_URL=fix_name_string_URL(name_string_URL),
                        dob=angio_study_vector[i]['patient_dob'],
                        sex=angio_study_vector[i]['patient_sex'],
                        dob_parsed=convert_date(angio_study_vector[i]['patient_dob']))
                    patient_model.save()

                    if angio_study_vector[i]['dose_PKA_total'] == 0 and angio_study_vector[i]['dose_KAPR_total'] == 0 and angio_study_vector[i]['fluoro_PKA_total'] == 0 and angio_study_vector[i]['fluoro_KAPR_total'] == 0 and angio_study_vector[i]['acq_PKA_total'] == 0 and angio_study_vector[i]['acq_KAPR_total'] == 0 and angio_study_vector[i]['fluoro_time_total'] == 0 and angio_study_vector[i]['acq_time_total'] == 0:
                        ModelDeletedUID.objects.get_or_create(del_uid=angio_study_vector[i]['series_uid'])

                    elif angio_study_vector[i]['series_uid'] not in [i['del_uid'] for i in list(ModelDeletedUID.objects.values('del_uid'))]:
                        # Cria estudo associado a paciente
                        study_model, created = ModelStudyXA.objects.get_or_create(
                            patient=patient_model,
                            uid=angio_study_vector[i]['series_uid'],
                            institution=angio_study_vector[i]['institution'],
                            study_date=angio_study_vector[i]['study_date'],
                            study_date_parsed=convert_date(angio_study_vector[i]['study_date']),
                            study_time=angio_study_vector[i]['study_time'],
                            study_time_parsed=convert_time(angio_study_vector[i]['study_time']),
                            dose_PKA_total=angio_study_vector[i]['dose_PKA_total'],
                            dose_KAPR_total=angio_study_vector[i]['dose_KAPR_total'],
                            fluoro_PKA_total=angio_study_vector[i]['fluoro_PKA_total'],
                            fluoro_KAPR_total=angio_study_vector[i]['fluoro_KAPR_total'],
                            acq_PKA_total=angio_study_vector[i]['acq_PKA_total'],
                            acq_KAPR_total=angio_study_vector[i]['acq_KAPR_total'],
                            fluoro_time_total=angio_study_vector[i]['fluoro_time_total'],
                            acq_time_total=angio_study_vector[i]['acq_time_total'])
                        study_model.save()

                        # Adiciona info de estudos ao paciente
                        if created:
                            patient_model.number_of_studies += 1
                            patient_model.dose_PKA_complete += decimal.Decimal(angio_study_vector[i]['dose_PKA_total'])
                            patient_model.dose_KAPR_complete += decimal.Decimal(angio_study_vector[i]['dose_KAPR_total'])
                            patient_model.save()
                        else:
                            print("Problema ao adicionar informacoes de estudos")

        else:
            print("Pedido passado.")
    return True


def create_models_by_date_fixed(number_of_days=1, number_of_months=0):
    # True = Query; False = pass
    query_or_pass = False

    name_vector = AngioGet.name_get_by_date_fixed([number_of_days, number_of_months], '10.5.136.10', 4096,
                                                  "projetoDoses", 'server-dicom', 'SR')

    # Obtem NOMES ainda nao presentes no banco de dados proprio (pedindo para servidor DICOM)
    name_needed = []
    lista = ModelPatient.objects.all().values('name').filter(name__in=name_vector)
    name_current_list = [name['name'] for name in lista]
    for name in name_vector:
        if name not in name_current_list:
            name_needed.append(name)
            query_or_pass = True

    # Cria request de nome em auxiliar
    while len(name_needed) > 0:
        if len(name_needed) > 40:
            name_string_block = name_needed[:40]
            name_needed = name_needed[40:]
        else:
            name_string_block = name_needed
            name_needed = []

        uid_study_vector = AngioGet.study_get(name_string_block, '10.5.136.10', 4096, "projetoDoses", 'server-dicom',
                                              'SR')
        # Obtem UID ainda nao presentes no banco de dados proprio (pedindo para servidor DICOM)
        uid_needed = []
        lista = ModelStudyXA.objects.all().values('uid').filter(uid__in=uid_study_vector)
        uid_current_list = [uid['uid'] for uid in lista]
        for uid in uid_study_vector:
            if uid not in uid_current_list:
                uid_needed.append(uid)
                query_or_pass = True

        # Se UID ainda nao presente em banco, obtem de servidor DICOM
        if query_or_pass:
            while len(uid_needed) > 0:
                if len(uid_needed) > 40:
                    uid_needed_block = uid_needed[:40]
                    uid_needed = uid_needed[40:]
                else:
                    uid_needed_block = uid_needed
                    uid_needed = []
                angio_study_vector = AngioGet.angio_get_by_uid(uid_needed_block, '10.5.136.10', 4096, "projetoDoses",
                                                               'server-dicom', 'SR')

                # Se obtem informaçao de Dose, adiciona em banco de dados
                if len(angio_study_vector) >= 1:

                    for i in range(len(angio_study_vector)):
                        # Adicona underline em nome para adiçao em URL
                        name_string_URL = angio_study_vector[i]['patient_name'].replace(' ', '_')

                        # Cria paciente
                        patient_model, created = ModelPatient.objects.get_or_create(
                            name=angio_study_vector[i]['patient_name'],
                            name_for_URL=fix_name_string_URL(name_string_URL),
                            dob=angio_study_vector[i]['patient_dob'],
                            sex=angio_study_vector[i]['patient_sex'],
                            dob_parsed=convert_date(angio_study_vector[i]['patient_dob']))
                        patient_model.save()

                        if angio_study_vector[i]['dose_PKA_total'] == 0 and angio_study_vector[i]['dose_KAPR_total'] == 0 and angio_study_vector[i]['fluoro_PKA_total'] == 0 and angio_study_vector[i]['fluoro_KAPR_total'] == 0 and angio_study_vector[i]['acq_PKA_total'] == 0 and angio_study_vector[i]['acq_KAPR_total'] == 0 and angio_study_vector[i]['fluoro_time_total'] == 0 and angio_study_vector[i]['acq_time_total'] == 0:
                            ModelDeletedUID.objects.get_or_create(del_uid=angio_study_vector[i]['series_uid'])

                        elif angio_study_vector[i]['series_uid'] not in [i['del_uid'] for i in list(ModelDeletedUID.objects.values('del_uid'))]:
                            # Cria estudo associado a paciente
                            study_model, created = ModelStudyXA.objects.get_or_create(
                                patient=patient_model,
                                uid=angio_study_vector[i]['series_uid'],
                                institution=angio_study_vector[i]['institution'],
                                study_date=angio_study_vector[i]['study_date'],
                                study_date_parsed=convert_date(angio_study_vector[i]['study_date']),
                                study_time=angio_study_vector[i]['study_time'],
                                study_time_parsed=convert_time(angio_study_vector[i]['study_time']),
                                dose_PKA_total=angio_study_vector[i]['dose_PKA_total'],
                                dose_KAPR_total=angio_study_vector[i]['dose_KAPR_total'],
                                fluoro_PKA_total=angio_study_vector[i]['fluoro_PKA_total'],
                                fluoro_KAPR_total=angio_study_vector[i]['fluoro_KAPR_total'],
                                acq_PKA_total=angio_study_vector[i]['acq_PKA_total'],
                                acq_KAPR_total=angio_study_vector[i]['acq_KAPR_total'],
                                fluoro_time_total=angio_study_vector[i]['fluoro_time_total'],
                                acq_time_total=angio_study_vector[i]['acq_time_total'])
                            study_model.save()

                            # Adiciona info de estudos ao paciente
                            if created:
                                patient_model.number_of_studies += 1
                                patient_model.dose_PKA_complete += decimal.Decimal(angio_study_vector[i]['dose_PKA_total'])
                                patient_model.dose_KAPR_complete += decimal.Decimal(angio_study_vector[i]['dose_KAPR_total'])
                                patient_model.save()

    return True


def create_models_by_date_period_fast(date_before, date_after):
    # True = Query; False = pass
    query_or_pass = False

    uid_study_vector = AngioGet.name_get_by_date_period_fast([date_before, date_after], '10.5.136.10', 4096,
                                                             "projetoDoses", 'server-dicom', 'SR')

    # Obtem UID ainda nao presentes no banco de dados proprio (pedindo para servidor DICOM)
    uid_needed = []
    lista = ModelStudyXA.objects.all().values('uid').filter(uid__in=uid_study_vector)
    uid_current_list = [uid['uid'] for uid in lista]
    for uid in uid_study_vector:
        if uid not in uid_current_list:
            uid_needed.append(uid)
            query_or_pass = True

    # Se UID ainda nao presente em banco, obtem de servidor DICOM
    if query_or_pass:

        while len(uid_needed) > 0:
            if len(uid_needed) > 40:
                uid_needed_block = uid_needed[:40]
                uid_needed = uid_needed[40:]
            else:
                uid_needed_block = uid_needed
                uid_needed = []

            angio_study_vector = AngioGet.angio_get_by_uid(uid_needed_block, '10.5.136.10', 4096, "projetoDoses",
                                                           'server-dicom', 'SR')
            # Se obtem informaçao de Dose, adiciona em banco de dados
            if len(angio_study_vector) >= 1:

                for i in range(len(angio_study_vector)):
                    # Adicona underline em nome para adiçao em URL
                    name_string_URL = angio_study_vector[i]['patient_name'].replace(' ', '_')
                    name_string_URL = name_string_URL.replace('^', '-')

                    # Cria paciente
                    patient_model, created = ModelPatient.objects.get_or_create(
                        name=angio_study_vector[i]['patient_name'],
                        name_for_URL=fix_name_string_URL(name_string_URL),
                        dob=angio_study_vector[i]['patient_dob'],
                        sex=angio_study_vector[i]['patient_sex'],
                        dob_parsed=convert_date(angio_study_vector[i]['patient_dob']))
                    patient_model.save()

                    if angio_study_vector[i]['dose_PKA_total'] == 0 and angio_study_vector[i]['dose_KAPR_total'] == 0 and angio_study_vector[i]['fluoro_PKA_total'] == 0 and angio_study_vector[i]['fluoro_KAPR_total'] == 0 and angio_study_vector[i]['acq_PKA_total'] == 0 and angio_study_vector[i]['acq_KAPR_total'] == 0 and angio_study_vector[i]['fluoro_time_total'] == 0 and angio_study_vector[i]['acq_time_total'] == 0:
                        ModelDeletedUID.objects.get_or_create(del_uid=angio_study_vector[i]['series_uid'])

                    elif angio_study_vector[i]['series_uid'] not in [i['del_uid'] for i in list(ModelDeletedUID.objects.values('del_uid'))]:

                        # Cria estudo associado a paciente
                        study_model, created = ModelStudyXA.objects.get_or_create(
                            patient=patient_model,
                            uid=angio_study_vector[i]['series_uid'],
                            institution=angio_study_vector[i]['institution'],
                            study_date=angio_study_vector[i]['study_date'],
                            study_date_parsed=convert_date(angio_study_vector[i]['study_date']),
                            study_time=angio_study_vector[i]['study_time'],
                            study_time_parsed=convert_time(angio_study_vector[i]['study_time']),
                            dose_PKA_total=angio_study_vector[i]['dose_PKA_total'],
                            dose_KAPR_total=angio_study_vector[i]['dose_KAPR_total'],
                            fluoro_PKA_total=angio_study_vector[i]['fluoro_PKA_total'],
                            fluoro_KAPR_total=angio_study_vector[i]['fluoro_KAPR_total'],
                            acq_PKA_total=angio_study_vector[i]['acq_PKA_total'],
                            acq_KAPR_total=angio_study_vector[i]['acq_KAPR_total'],
                            fluoro_time_total=angio_study_vector[i]['fluoro_time_total'],
                            acq_time_total=angio_study_vector[i]['acq_time_total'])
                        study_model.save()

                        # Adiciona info de estudos ao paciente
                        if created:
                            patient_model.number_of_studies += 1
                            patient_model.dose_PKA_complete += decimal.Decimal(angio_study_vector[i]['dose_PKA_total'])
                            patient_model.dose_KAPR_complete += decimal.Decimal(angio_study_vector[i]['dose_KAPR_total'])
                            patient_model.save()

    return True


def update_models_by_name(name_string):
    # True = Query; False = pass
    query_or_pass = True

    while len(name_string) > 0:
        if len(name_string) > 40:
            name_string_block = name_string[:40]
            name_string = name_string[40:]
        else:
            name_string_block = name_string
            name_string = []

        uid_study_vector = AngioGet.study_get(name_string_block, '10.5.136.10', 4096, "projetoDoses", 'server-dicom', 'SR')

        # Se UID ainda nao presente em banco, obtem de servidor DICOM
        if query_or_pass:

            while len(uid_study_vector) > 0:
                if len(uid_study_vector) > 40:
                    uid_study_vector_block = uid_study_vector[:40]
                    uid_study_vector = uid_study_vector[40:]
                else:
                    uid_study_vector_block = uid_study_vector
                    uid_study_vector = []

                angio_study_vector = AngioGet.angio_get_by_uid(uid_study_vector_block, '10.5.136.10', 4096,
                                                               "projetoDoses", 'server-dicom', 'SR')

                # Se obtem informaçao de Dose, adiciona em banco de dados
                if len(angio_study_vector) >= 1:

                    for i in range(len(angio_study_vector)):

                        # Cria estudo associado a paciente
                        study_query = ModelStudyXA.objects.all().filter(uid=angio_study_vector[i]['series_uid'])
                        for study_model in study_query:
                            study_model.institution = angio_study_vector[i]['institution']
                            study_model.study_date = angio_study_vector[i]['study_date']
                            study_model.study_date_parsed = convert_date(angio_study_vector[i]['study_date'])
                            study_model.study_time = angio_study_vector[i]['study_time']
                            study_model.study_time_parsed = convert_time(angio_study_vector[i]['study_time']).isoformat()
                            study_model.dose_PKA_total = angio_study_vector[i]['dose_PKA_total']
                            study_model.dose_KAPR_total = angio_study_vector[i]['dose_KAPR_total']
                            study_model.fluoro_PKA_total = angio_study_vector[i]['fluoro_PKA_total']
                            study_model.fluoro_KAPR_total = angio_study_vector[i]['fluoro_KAPR_total']
                            study_model.acq_PKA_total = angio_study_vector[i]['acq_PKA_total']
                            study_model.acq_KAPR_total = angio_study_vector[i]['acq_KAPR_total']
                            study_model.fluoro_time_total = angio_study_vector[i]['fluoro_time_total']
                            study_model.acq_time_total = angio_study_vector[i]['acq_time_total']

                            study_model.save()

                            print("Estudo atualizado!")

        else:
            print("Pedido passado.")
    return True


def statistics(vec):

    stats_dict = {}
    if len(vec) > 0:
        stats_dict['mean'] = (sum(vec) / len(vec))
        stats_dict['std'] = std(vec)
        stats_dict['med'] = median(vec)
    else:
        stats_dict['mean'] = 0
        stats_dict['std'] = 0
        stats_dict['med'] = 0
    return stats_dict

def statistic_by_date(study_vec):

    stats_vec = [[] for _ in range(8)]
    for i in study_vec:
        stats_vec[0].append(i.fluoro_time_total)
        stats_vec[1].append(i.acq_time_total)
        stats_vec[2].append(i.fluoro_PKA_total)
        stats_vec[3].append(i.fluoro_KAPR_total)
        stats_vec[4].append(i.acq_PKA_total)
        stats_vec[5].append(i.acq_KAPR_total)
        stats_vec[6].append(i.dose_PKA_total)
        stats_vec[7].append(i.dose_KAPR_total)

    all_dict = {}
    all_dict['t_flu'] = statistics(stats_vec[0])
    all_dict['t_acq'] = statistics(stats_vec[1])
    all_dict['PKA_flu'] = statistics(stats_vec[2])
    all_dict['KAPR_flu'] = statistics(stats_vec[3])
    all_dict['PKA_acq'] = statistics(stats_vec[4])
    all_dict['KAPR_acq'] = statistics(stats_vec[5])
    all_dict['PKA_tot'] = statistics(stats_vec[6])
    all_dict['KAPR_tot'] = statistics(stats_vec[7])
    return all_dict


def database_update(data_present=False, date='9999-99-99'):

    name_string = list(ModelPatient.objects.all().values_list('name', flat=True))

    created = update_models_by_name(name_string)
    #created = create_models_by_name(name_string)
    if created:
        print('All models created successfully')
    elif created == False:
        print('No studies received from patient data')
    else:
        print('Query passed')

    if not data_present:
        created = create_models_by_date_fixed(number_of_days=1, number_of_months=0)
        if created:
            print('All models created successfully')
        elif created == False:
            print('No studies received from patient data')
        else:
            print('Query passed')
    else:
        parsed_date = convert_date_dash(date)
        today_date = datetime.date.today()
        delta = today_date - parsed_date
        created = create_models_by_date_fixed(number_of_days=delta.days, number_of_months=0)
        if created:
            print('All models created successfully')
        elif created == False:
            print('No studies received from patient data')
        else:
            print('Query passed')

    return True


def program_update():
    print('Updating...')
    my_repo = git.Repo(".")
    my_repo.config_reader()
    try:
        print('adding...')
        my_repo.git.add("--all")
        
        print('commiting...')
        my_repo.git.commit("-m 'auto commit'")
        
        print('pushing...')
        o = my_repo.remotes.origin
        o.push('master')
        
    except:
        pass

    o = my_repo.remotes.upd 
    # print('fetch')
    # o.fetch("master", f=True)
    print('pulling...')
    o.pull("master", X="theirs", force=True, ff=True)
    print("Updated!")
    return True

