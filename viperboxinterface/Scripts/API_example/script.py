import time

import requests
from lxml import etree


def _wait_script(start_time: float, initial_time: float):
    while time.time() - float(initial_time) < float(start_time):
        time.sleep(0.01)
    return True


def to_settings_xml_string(settings_input: dict) -> str:
    program = etree.Element("Program")
    settings = etree.SubElement(program, "Settings")
    settings_type = {
        "Channel": "RecordingSettings",
        "Configuration": "StimulationWaveformSettings",
        "Mapping": "StimulationMappingSettings",
    }

    for sub_type, dct in settings_input.items():
        recording_settings = etree.SubElement(settings, settings_type[sub_type])
        _ = etree.SubElement(recording_settings, sub_type, attrib=dct)

    return etree.tostring(program).decode("utf-8")


def upload_settings(settings, time_init, viperbox_url):
    _wait_script(settings["start_time"], time_init)
    xml_string = to_settings_xml_string(
        settings_input={
            "Channel": {
                "box": "1",
                "probe": "1",
                "channel": "-",
                "references": "b",
                "gain": "0",
                "input": "0",
            },
        },
    )
    data = {
        "recording_XML": xml_string,
        "reset": "False",
        "default_values": "False",
    }
    _ = requests.post(
        viperbox_url + "recording_settings",
        json=data,
        timeout=5,
    )

    stimulation_xml = to_settings_xml_string(
        settings_input={
            "Configuration": {
                "box": "1",
                "probe": "1",
                "stimunit": "1",
                "polarity": "0",
                "pulses": settings["pulses"],
                "prephase": "0",
                "amplitude1": "1",
                "width1": "170",
                "interphase": "60",
                "amplitude2": "1",
                "width2": "170",
                "discharge": "200",
                "duration": settings["duration"],
                "aftertrain": "0",
            },
            "Mapping": {
                "box": "-",
                "probe": "-",
                "stimunit": "1",
                "electrodes": settings["electrodes"],
            },
        },
    )
    data = {
        "stimulation_XML": stimulation_xml,
        "reset": "False",
        "default_values": "False",
    }
    _ = requests.post(
        viperbox_url + "stimulation_settings",
        json=data,
        timeout=5,
    )


def start_recording(recording_file_name, viperbox_url):
    data = {"recording_name": recording_file_name}
    _ = requests.post(viperbox_url + "start_recording", json=data, timeout=5)


def stimulate(settings, time_init, viperbox_url):
    _wait_script(settings["start_time"], time_init)
    data = {"boxes": "1", "probes": "-", "SU_input": "1"}
    _ = requests.post(viperbox_url + "start_stimulation", json=data, timeout=5)


def stop_recording(settings, time_init, viperbox_url):
    _wait_script(settings["start_time"], time_init)
    _ = requests.post(viperbox_url + "stop_recording")


viperbox_url = "http://127.0.0.1:8000/"
recording_file_name = "test_recording"
settings_1 = {
    "start_time": "0.0",
    "duration": "3000",
    "pulses": "50",
    "electrodes": "85",
}
stimulation_1 = {
    "start_time": "5.0",
}

settings_2 = {
    "start_time": "10.0",
    "duration": "6000",
    "pulses": "50",
    "electrodes": "85",
}
stimulation_2 = {
    "start_time": "15.0",
}

settings_3 = {
    "start_time": "20.0",
    "duration": "1500",
    "pulses": "50",
    "electrodes": "85",
}
stimulation_3 = {
    "start_time": "25.0",
}

stop = {
    "start_time": "27.0",
}
print("Starting script")
print("Starting recording")
start_recording(recording_file_name, viperbox_url)
time_init = time.time()
print("Uploading settings 1")
upload_settings(settings_1, time_init, viperbox_url)
print("Starting stimulation 1")
stimulate(stimulation_1, time_init, viperbox_url)
print("Uploading settings 2")
upload_settings(settings_2, time_init, viperbox_url)
print("Starting stimulation 2")
stimulate(stimulation_2, time_init, viperbox_url)
print("Uploading settings 3")
upload_settings(settings_3, time_init, viperbox_url)
print("Starting stimulation 3")
stimulate(stimulation_3, time_init, viperbox_url)
print("Stopping recording")
stop_recording(stop, time_init, viperbox_url)
print("Script finished")
