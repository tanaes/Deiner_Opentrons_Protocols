from opentrons import protocol_api
from numpy import floor
from itertools import chain

metadata = {
    'apiLevel': '2.8',
    'author': 'Jon Sanders'}

# Define parameters for protocol

###### Sample Plates ######

# Define sample plates and their corresponding tip racks.
sample_plates = {'Plate 1': {'pos': 1,
                             'tip': 7},
                 'Plate 2': {'pos': 2,
                             'tip': 8}}

# Define columns to transfer for PCR
sample_cols = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6',
               'A7', 'A8', 'A9', 'A10', 'A11', 'A12']


###### PCR Plates #######

# Define PCR plate positions.
pcr_plates = {'PCR 1': 3,
              'PCR 2': 4,
              'PCR 3': 5,
              'PCR 4': 6}

# Define MM location for each PCR plate.
pcr_mm_map = {'PCR 1': 'A1',
              'PCR 2': 'A2',
              'PCR 3': 'A3',
              'PCR 4': 'A4'
              }

###### Sample:PCR map #######

# Link each sample plate to the PCR plate replicates
sample_pcr_map = {'Plate 1': ['PCR 1',
                              'PCR 2'],
                  'Plate 2': ['PCR 3',
                              'PCR 4']}

# Sample and PCR plate types
sample_labware = 'biorad_96_wellplate_200ul_pcr'
pcr_labware = 'biorad_96_wellplate_200ul_pcr'

# PCR master mix and sample volumes
mm_vol = 8
sample_vol = 2

def run(protocol: protocol_api.ProtocolContext):

    # define deck positions and labware

    # tips
    tiprack_reagents = protocol.load_labware('opentrons_96_filtertiprack_200ul', 9)

    # reagents
    reagents = protocol.load_labware('usascientific_12_reservoir_22ml',
                                     11, 'reagents')

    # sample plates and tips

    sample_obj = {}
    sample_tips = {}
    pcr_obj = {}
    for s in sample_plates:
        sample_obj[s] = protocol.load_labware(sample_labware,
                                              sample_plates[s]['pos'],
                                              s)
        sample_tips[s] = protocol.load_labware('opentrons_96_filtertiprack_20ul',
                                              sample_plates[s]['tip'],
                                              s)
    for p in pcr_plates:
        pcr_obj[p] = protocol.load_labware(pcr_labware,
                                           pcr_plates[p],
                                           p)

    # initialize pipettes
    pipette_left = protocol.load_instrument('p20_multi_gen2',
                                             'left')
    pipette_right = protocol.load_instrument('p300_multi_gen2',
                                             'right',
                                             tip_racks=[tiprack_reagents])

    # # home instrument
    protocol.home()

    # # dispense master mix
    for p in pcr_plates:
        print(p)
        print(pcr_obj[p])
        pipette_right.distribute(mm_vol,
                                 reagents[pcr_mm_map[p]], 
                                 [pcr_obj[p][c] for c in sample_cols],
                                 blow_out=False,
                                 blowout_location='source well',
                                 disposal_volume=10)

    # Dispense samples
    for s in sample_plates:
        for c in sample_cols:
            print(sample_tips[s][c])
            pipette_left.pick_up_tip(sample_tips[s][c])
            pipette_left.distribute(sample_vol,
                                    sample_obj[s][c],
                                    [pcr_obj[p][c].bottom() for p in sample_pcr_map[s]],
                                    new_tip='never',
                                    blow_out=False,
                                    disposal_volume=1,
                                    trash=False)
            pipette_left.drop_tip()


