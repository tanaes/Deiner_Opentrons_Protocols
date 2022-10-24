#!./libs/bats/bin/bats

@test "Testing Hackflex full plate protocol" {
  run opentrons_simulate \
       -L ../Labware/custom_labware \
       ../Extraction/mag_bead_extraction/mag_bead_extraction-part_B.py \
       > test_Hackflex.out 2>&1
  echo "status = ${status}"
  echo "output = ${output}"
  [ "$status" -eq 0 ]
}