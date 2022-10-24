# PCR setup

This protocol automates the setup of one or more PCRs from one or more sample plates.

The protocol is designed to be flexible, allowing you to easily modify some variables to determine how the PCR is set up. 


## Buffers and Reagents

### PCR master mix

Volume depends on protocol

## Equipment
### OpenTrons equipment

- OT-2 robot
- Multi channel P300 pipette
- Multi channel P20 pipette


## Consumables

- 1x Opentrons 200 µL filtertips (reagents)
- `P` BioRad hard-shell PCR plates, where `P` is the number of PCR plates used
- `S` Opentrons 20 µL filtertips (samples), where `S` is the number of sample plates


## Setup

### Deck layout

![Part A deck layout](./deckmap_magbead_A.png)

## Protocol Modification

To set up the protocol, you will need to modify variables at the top of the protocol file. 

### Sample plates and columns

Specify sample plates by modifying the following section:

```

###### Sample Plates ######

# Define sample plates and their corresponding tip racks.
sample_plates = {'Plate 1': {'pos': 1,
                             'tip': 7},
                 'Plate 2': {'pos': 2,
                             'tip': 8}}

# Define columns to transfer for PCR
sample_cols = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6',
               'A7', 'A8', 'A9', 'A10', 'A11', 'A12']

```

You will add a row to the `sample_plates` dictionary definition for each sample
plate. Make sure the sample plate name is in single or double quotes! Specify
the deck slot location for the sample plate using `'pos': X'`, and the deck slot
position for that sample plate's p20 filter tip rack using `'tip': Y`.

You can reduce the number of columns used by deleting entries from the 
`sample_cols` list.

### PCR plates and master mixes

Specify the PCR plates to be produced by modifying the following section:

```
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
```

Here, the dictionary `pcr_plates` is just specifying the deck slot position for
each PCR plate. 

You can determine which well of the reagents well plate will be used for each 
PCR plate by modifying `pcr_mm_map`. In this example, each PCR plate gets its
own master mix from a separate well. This can be useful if, for example, you 
need to use a different primer set for each PCR plate.

### Sample:PCR map

Specify the mapping of sample plates to PCR plates by modifying the following:

```
# Link each sample plate to the PCR plate replicates
sample_pcr_map = {'Plate 1': ['PCR 1',
                              'PCR 2'],
                  'Plate 2': ['PCR 3',
                              'PCR 4']}

```

In this example, sample plate `'Plate 1'` will be duplicated in PCR plates `'PCR 1'` and `'PCR 2'`, and sample plate `'Plate 2'` will be duplicated in PCR plates `'PCR 3'` and `'PCR 4'`. There **must** be an entry in this dictionary for each sample plate! Note that both the sample plate and PCR plate names are in quotes, and much match their names as defined in the preceding sections.

### Plate types and sample volumes

Finally, you can modify the types of plates used and the volumes of master mix or sample to transfer by modifying the following:

```
# Sample and PCR plate types
sample_labware = 'biorad_96_wellplate_200ul_pcr'
pcr_labware = 'biorad_96_wellplate_200ul_pcr'

# PCR master mix and sample volumes
mm_vol = 8
sample_vol = 2
```

## Protocol

Place plate of homogenate supernatants (output of Part A) onto the magdeck in position 10. Press go. 

Once the robot has transferred beads and hybridization solution to the deep-well plate, it will pause the protocol. Remove the plate, seal it, and place it on the rotator for ten minutes. Then, remove the seal and place back on the magnetic module. The remainder of the protocol is automated.
