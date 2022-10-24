from opentrons import protocol_api
from numpy import floor
from itertools import chain

metadata = {
    'apiLevel': '2.8',
    'author': 'Jon Sanders'}

# Define parameters for protocol

###### Index Plates ######

# Define sample plates and their corresponding tip racks.
index_plates = {'idx 1': {'pos': 7,
                            'tip': 4},
                'idx 2': {'pos': 8,
                            'tip': 5},
                'idx 3': {'pos': 9,
                            'tip': 6}}

# Define columns to transfer for PCR
sample_cols = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6',
               'A7', 'A8', 'A9', 'A10', 'A11', 'A12']


###### PCR Plates #######

# Define PCR plate positions.
pcr_plates = {'PCR 1': 1,
              'PCR 2': 2,
              'PCR 3': 3}

# Define MM location for each PCR plate.
pcr_mm_map = {'PCR 1': 'A1',
              'PCR 2': 'A2',
              'PCR 3': 'A3'
              }

###### Index:PCR map #######

# Link each index plate to the PCR plate replicates
index_pcr_map = {'idx 1': ['PCR 1'],
                 'idx 2': ['PCR 2'],
                 'idx 3': ['PCR 3']}

# Index and PCR plate types
index_labware = 'biorad_96_wellplate_200ul_pcr'
pcr_labware = 'biorad_96_wellplate_200ul_pcr'

# PCR master mix and index volumes
mm_vol = 11.5
index_vol = 1.5

def run(protocol: protocol_api.ProtocolContext):

    # define deck positions and labware

    # tips
    tiprack_reagents = protocol.load_labware('opentrons_96_filtertiprack_200ul', 10)

    # reagents
    reagents = protocol.load_labware('usascientific_12_reservoir_22ml',
                                     11, 'reagents')

    # sample plates and tips

    index = {}
    index_tips = {}
    pcr_obj = {}
    for i in index_plates:
        index[i] = protocol.load_labware(index_labware,
                                              index_plates[i]['pos'],
                                              i)
        index_tips[i] = protocol.load_labware('opentrons_96_filtertiprack_20ul',
                                              index_plates[i]['tip'],
                                              i)
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
    for i in index_plates:
        for c in sample_cols:
            print(index_tips[i][c])
            pipette_left.pick_up_tip(index_tips[i][c])
            pipette_left.distribute(index_vol,
                                    index[i][c],
                                    [pcr_obj[p][c].bottom() for p in index_pcr_map[i]],
                                    new_tip='never',
                                    blow_out=False,
                                    disposal_volume=1,
                                    trash=False)
            pipette_left.drop_tip()


