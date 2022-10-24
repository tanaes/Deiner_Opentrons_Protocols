# Index PCR setup

This protocol automates the setup of one or more secondary PCRs from one or more index plates.

The protocol is designed to be flexible, allowing you to easily modify some variables to determine how the PCR is set up. 


## Buffers and Reagents

### PCR master mix

Volume depends on protocol

### Index primer plates

Number and volume depends on protocol

## Equipment
### OpenTrons equipment

- OT-2 robot
- Multi channel P300 pipette
- Multi channel P20 pipette


## Consumables

- 1x Opentrons 200 µL filtertips (reagents)
- `I` BioRad hard-shell PCR plates, where `I` is the number of index plates used
- `I` Opentrons 20 µL filtertips (indices), where`I` is the number of index plates


## Setup

### Deck layout

![Part A deck layout](./deckmap_magbead_A.png)

## Protocol Modification

To set up the protocol, you will need to modify variables at the top of the protocol file. 

### Index plates and columns

Specify index plates by modifying the following section:

```
###### Index Plates ######

# Define index plates and their corresponding tip racks.
index_plates = {'idx 1': {'pos': 7,
                            'tip': 4},
                'idx 2': {'pos': 8,
                            'tip': 5},
                'idx 3': {'pos': 9,
                            'tip': 6}}

# Define columns to transfer for PCR
sample_cols = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6',
               'A7', 'A8', 'A9', 'A10', 'A11', 'A12']

```

You will add a row to the `index_plates` dictionary definition for each index
plate. Make sure the index plate name is in single or double quotes! Specify
the deck slot location for the index plate using `'pos': X'`, and the deck slot
position for that index plate's p20 filter tip rack using `'tip': Y`.

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

### Index:PCR map

Specify the mapping of index plates to PCR plates by modifying the following:

```
###### Index:PCR map #######

# Link each index plate to the PCR plate replicates
index_pcr_map = {'idx 1': ['PCR 1'],
                 'idx 2': ['PCR 2'],
                 'idx 3': ['PCR 3']}

```

In this example, index plate `'idx 1'` will be transferred to PCR plate `'PCR 1'`,  index plate `'idx 2'` will be transferred to PCR plate `'PCR 2'`,  and index plate `'idx 3'` will be transferred to PCR plate `'PCR 3'`. There **must** be an entry in this dictionary for each index plate! Note that both the index plate and PCR plate names are in quotes, and much match their names as defined in the preceding sections.

You can use a single index plate for multiple PCR plates by adding PCR plates to the list in the dictionary. For example:

```

# Link each index plate to the PCR plate replicates
index_pcr_map = {'idx 1': ['PCR 1', 
                           'PCR 2',
                           'PCR 3']}

```

will use indices from index plate 1 for all three PCR plates. 

### Plate types and index volumes

Finally, you can modify the types of plates used and the volumes of master mix or index to transfer by modifying the following:

```
# index and PCR plate types
index_labware = 'biorad_96_wellplate_200ul_pcr'
pcr_labware = 'biorad_96_wellplate_200ul_pcr'

# PCR master mix and index volumes
mm_vol = 8
index_vol = 2
```
