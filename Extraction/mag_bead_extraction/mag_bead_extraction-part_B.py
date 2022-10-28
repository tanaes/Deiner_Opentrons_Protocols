



from opentrons import protocol_api
from opentrons_functions.magbeads import (
    remove_supernatant, bead_wash, bead_mix)
from opentrons_functions.transfer import add_buffer


metadata = {'apiLevel': '2.8',
            'author': 'Jon Sanders'}

# Set to `True` to perform a short run, with brief pauses and only
# one column of samples
test_run = False

if test_run:
    pause_eth_bind = 5
    pause_aq_bind = 3
    pause_dry = 30
    pause_elute = 5

    # Limit columns
    cols = ['A1']
else:
    pause_eth_bind = 5*60
    pause_aq_bind = 10*60
    pause_dry = 20*60
    pause_elute = 7*60

    # Limit columns
    cols = ['A1']
    # cols = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6',
    #         'A7', 'A8', 'A9', 'A10', 'A11', 'A12']


# Lysate transfer volume

lysate_vol = 425

wash_vol = 290

rinse_vol = 800

elute_vol = 100

elute_mix_num = 15

# fill volumes

eth_well_vol = 40000

hyb_well_vol = 40000

# define magnet engagement height for plates
# (none if using labware with built-in specs)
mag_engage_height = 11


# REAGENTS plate:
# Bead columns
bead_cols = ['A1']

# Elute col
elute_col = 'A6'


# WASH plate:

# Ethanol columns
eth_cols = ['A1','A2', 'A3', 'A4']


# bead aspiration flow rate
bead_flow = .25

# wash mix mutliplier
wash_mix = 5


# function relating volume to liquid height in magplate
def vol_fn(x):
    return(x/(3.14 * 3**2))


def run(protocol: protocol_api.ProtocolContext):

    # ### Setup

    # define deck positions and labware

    # define hardware modules
    magblock = protocol.load_module('magnetic module', 6)
    magblock.disengage()

    # tips
    tiprack_buffers = protocol.load_labware('opentrons_96_tiprack_300ul',
                                            7)
    tiprack_elution = protocol.load_labware(
                            'opentrons_96_filtertiprack_200ul', 4)
    tiprack_wash1 = protocol.load_labware('opentrons_96_tiprack_300ul',
                                          5)
    tiprack_wash2 = protocol.load_labware('opentrons_96_tiprack_300ul',
                                          8)
    # tiprack_wash3 = protocol.load_labware('opentrons_96_tiprack_300ul',
    #                                       9)
    # tiprack_wash4 = protocol.load_labware('opentrons_96_tiprack_300ul',
    #                                       4)

    # plates
    eluate = protocol.load_labware('biorad_96_wellplate_200ul_pcr',
                                   10, 'eluate')
    waste = protocol.load_labware('nest_1_reservoir_195ml',
                                  9, 'liquid waste')
    reagents = protocol.load_labware('brand_6_reservoir_40000ul',
                                     2, 'reagents')
    wash = protocol.load_labware('brand_6_reservoir_40000ul',
                                     1, 'wash buffers')

    samples = protocol.load_labware('brand_96_wellplate_1200ul',
                                     3, 'samples')
    # load plate on magdeck
    # mag_plate = magblock.load_labware('vwr_96_wellplate_1000ul')
    mag_plate = magblock.load_labware('brand_96_wellplate_1200ul')

    # initialize pipettes
    pipette_left = protocol.load_instrument('p300_multi_gen2',
                                            'left',
                                            tip_racks=[tiprack_buffers])

    # SeraMag bead wells
    bead_wells = [reagents[x] for x in bead_cols]

    # Ethanol columns
    eth_wells = [wash[x] for x in eth_cols]

    # temporarily decrease movement speed to minimize mess
    pipette_left.default_speed = 200


    ### Adding beads

    hyb_vol = 0.66 * lysate_vol

    bead_mix(pipette_left,
             reagents,
             bead_cols,
             None,
             n=10,
             z_offset=2,
             mix_vol=300,
             mix_lift=20,
             drop_tip=True)

    # add beads
    bead_remaining, bead_wells = add_buffer(pipette_left,
                                            bead_wells,
                                            samples,
                                            cols,
                                            hyb_vol,
                                            hyb_well_vol/8)


    # ### Prompt user to place plate on rotator
    protocol.pause('Seal sample plate and place on rotator. Rotate at low '
                   'speed for 10 minutes.')

    protocol.delay(seconds=1)

    protocol.pause('Now spin down plate, unseal, and place back on '
                   'position 3.')


    # add samples

    subset_vol = (lysate_vol+hyb_vol)/2

    for col in cols:
        pipette_left.pick_up_tip(tiprack_wash1.wells_by_name()[col])
        pipette_left.transfer(subset_vol,
                              samples.wells_by_name()[col],
                              mag_plate.wells_by_name()[col],
                              rate=1,
                              air_gap=5,
                              new_tip='never')
        pipette_left.return_tip()

    # bind to magnet
    protocol.comment('Binding beads to magnet.')
    magblock.engage(height_from_base=mag_engage_height)

    protocol.delay(seconds=pause_aq_bind)

    # remove supernatant
    remove_supernatant(pipette_left,
                       mag_plate,
                       cols,
                       tiprack_wash1,
                       waste['A1'],
                       super_vol=subset_vol - 5,
                       tip_vol=300,
                       rate=bead_flow,
                       bottom_offset=1,
                       drop_tip=False)

    # add samples
    for col in cols:
        pipette_left.pick_up_tip(tiprack_wash1.wells_by_name()[col])
        pipette_left.transfer(subset_vol,
                              samples.wells_by_name()[col],
                              mag_plate.wells_by_name()[col],
                              rate=1,
                              mix_before=(2,200),
                              air_gap=5,
                              new_tip='never')
        pipette_left.return_tip()

    protocol.delay(seconds=pause_aq_bind)


    # remove supernatant
    remove_supernatant(pipette_left,
                       mag_plate,
                       cols,
                       tiprack_wash1,
                       waste['A1'],
                       super_vol=subset_vol - 5,
                       tip_vol=300,
                       rate=bead_flow,
                       bottom_offset=1,
                       drop_tip=True)

    pipette_left.default_speed = 400


    # Rinse well with ethanol

    eth_remaining, eth_wells = add_buffer(pipette_left,
                                          eth_wells,
                                          mag_plate,
                                          cols,
                                          rinse_vol,
                                          eth_well_vol/8)

    remove_supernatant(pipette_left,
                       mag_plate,
                       cols,
                       tiprack_wash2,
                       waste['A1'],
                       super_vol=rinse_vol,
                       tip_vol=300,
                       rate=1,
                       bottom_offset=1,
                       drop_tip=False)

    # ### Do first wash: Wash 800 µL EtOH
    protocol.comment('Doing wash #1.')
    eth_remaining, eth_wells = bead_wash(
                                       # global arguments
                                       protocol,
                                       magblock,
                                       pipette_left,
                                       mag_plate,
                                       cols,
                                       # super arguments
                                       waste['A1'],
                                       tiprack_wash2,
                                       # wash buffer arguments
                                       eth_wells,
                                       eth_well_vol/8,
                                       # mix arguments
                                       tiprack_wash2,
                                       drop_mix_tip=False,
                                       # optional arguments,
                                       wash_vol=wash_vol,
                                       super_vol=wash_vol,
                                       super_tip_vol=300,
                                       super_blowout=False,
                                       drop_super_tip=False,
                                       rate=1,
                                       vol_fn=vol_fn,
                                       mix_n=wash_mix,
                                       mix_vol=290,
                                       mix_lift=0,
                                       remaining=None,
                                       mag_engage_height=mag_engage_height,
                                       pause_s=pause_eth_bind)

    # iterate to next full well
    # if eth_remaining < eth_well_vol:
    #     eth_wells.pop(0)

    # protocol.pause('Replace empty tip box in position 9 with new tips.')

    # ### Do second wash: Wash 800 µL EtOH
    protocol.comment('Doing wash #2.')
    eth_remaining, eth_wells = bead_wash(
                                       # global arguments
                                       protocol,
                                       magblock,
                                       pipette_left,
                                       mag_plate,
                                       cols,
                                       # super arguments
                                       waste['A1'],
                                       tiprack_wash2,
                                       # wash buffer arguments
                                       eth_wells,
                                       eth_well_vol/8,
                                       # mix arguments
                                       tiprack_wash2,
                                       drop_mix_tip=False,
                                       # optional arguments,
                                       wash_vol=wash_vol - 50,
                                       super_vol=wash_vol,
                                       super_tip_vol=300,
                                       super_blowout=True,
                                       drop_super_tip=False,
                                       rate=1,
                                       vol_fn=vol_fn,
                                       mix_n=wash_mix,
                                       mix_vol=290,
                                       mix_lift=0,
                                       remaining=eth_remaining,
                                       mag_engage_height=mag_engage_height,
                                       pause_s=pause_eth_bind)

    # ### Dry
    protocol.comment('Removing wash and drying beads.')

    # This should:
    # - pick up tip in position 8
    # - pick up supernatant from magplate
    # - dispense in waste, position 11
    # - repeat
    # - trash tip
    # - leave magnet engaged

    # protocol.pause('Replace empty tip box in position 4 with new tips.')

    # remove supernatant
    remove_supernatant(pipette_left,
                       mag_plate,
                       cols,
                       tiprack_wash2,
                       waste['A1'],
                       super_vol=wash_vol,
                       tip_vol=300,
                       rate=bead_flow,
                       bottom_offset=.2,
                       drop_tip=True)

    # dry
    protocol.delay(seconds=pause_dry)

    # ### Elute
    protocol.comment('Eluting DNA from beads.')

    # This should:
    # - disengage magnet
    # - pick up tip from position 6
    # - pick up reagents from column 2 of position 9
    # - dispense into magplate
    # - mix 10 times
    # - blow out, touch tip
    # - return tip to position 6
    # - wait (5 seconds)
    # - engage magnet
    # - wait (5 seconds)
    # - pick up tip from position 6
    # - aspirate from magplate
    # - dispense to position 3
    # - trash tip

    # transfer elution buffer to mag plate
    magblock.disengage()

    # add elution buffer and mix
    for col in cols:
        pipette_left.pick_up_tip(tiprack_elution.wells_by_name()[col])
        pipette_left.aspirate(elute_vol, reagents[elute_col], rate=1)
        pipette_left.dispense(elute_vol, mag_plate[col].bottom(z=1))
        pipette_left.mix(elute_mix_num, elute_vol - 10, mag_plate[col].bottom(z=1))
        pipette_left.blow_out(mag_plate[col].top())
        pipette_left.touch_tip()
        # we'll use these same tips for final transfer
        pipette_left.return_tip()

    protocol.delay(seconds=pause_elute)
    # # start timer
    # t0 = clock()
    # # mix again
    # t_mix = 0
    # while t_mix < pause_elute():
    for col in cols:
        pipette_left.pick_up_tip(tiprack_elution.wells_by_name()[col])
        pipette_left.mix(elute_mix_num, elute_vol - 10, mag_plate[col].bottom(z=1))
        pipette_left.blow_out(mag_plate[col].top())
        pipette_left.touch_tip()
        # we'll use these same tips for final transfer
        pipette_left.return_tip()
        # t_mix = clock() - t0

    # bind to magnet
    protocol.comment('Binding beads to magnet.')

    magblock.engage(height_from_base=mag_engage_height)

    protocol.delay(seconds=pause_aq_bind)

    protocol.comment('Transferring eluted DNA to final plate.')
    for col in cols:
        pipette_left.pick_up_tip(tiprack_elution.wells_by_name()[col])
        pipette_left.aspirate(elute_vol,
                              mag_plate[col].bottom(z=2),
                              rate=bead_flow)
        pipette_left.dispense(elute_vol, eluate[col])
        pipette_left.blow_out(eluate[col].top())
        pipette_left.touch_tip()
        # we're done with these tips now
        pipette_left.drop_tip()

    magblock.disengage()
