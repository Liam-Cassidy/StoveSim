# -*- coding: utf-8 -*-
"""
Created on Mon Apr 22 15:52:06 2019

@author: Lee
"""


#from import_geometry import *
import os
import fileinput
import shutil

""" Command line arguments:"""
# Import necessary packages
import sys
import argparse
import yaml
import time
from time import sleep


import readArgumentsRaw
from readArgumentsRaw import convert_namespace, pull_input_data

import argument_processor
from argument_processor import create_1d_angle_array_RHS, create_1d_angle_array_LHS, create_1D_velocity_magnitude_array_RHS, compute_number_of_simulations, create_empty_simulation_array, fill_simulation_array

import boundary_conditions
from boundary_conditions import calculate_fuel_mass_flow

import Geometry_and_Mesh_Definition
from Geometry_and_Mesh_Definition import x_coordinates, y_coordinates, z_coordinates, create_coordinate_strings, determine_working_directory, find_block_mesh_template, write_mesh_0422

import case_setup
from case_setup import create_simulations_folder, create_case_directories, paste_static_foam_files, add_foam_directories


def main():
    """ Main script"""
    # Static for now, stick definitions:
    stick_width = 0.01
    stick_height = 0.04


    # Construct the argument parse and parse the arguments
    parser = argparse.ArgumentParser(description='StoveSim')
    # File directory argument
    parser.add_argument('-i','--inputfile', required=True, help='Please enter the full file path (directory and filename.extension) in Linux format for the input.yaml file in LINUX format. For example, /mnt/c/Oregon_State/Spring_2019/Soft_dev_eng/StoveOpt/StoveOpt/inputFiles/input.yaml')
    import sys
    args = parser.parse_args(sys.argv[1:])

    # Reading arguments raw
    input_file = convert_namespace(args)
    D_fd, H_fd, Dc, H_cc, L_deck, h_deck_pot, number_of_angles_analyzed, number_of_flowrates_analyzed, lower_angle_design_value, lower_flowrate_design_value, upper_angle_design_value, upper_flowrate_design_value, Firepower, LHV = pull_input_data(input_file)


    # Compute boundary conditions:
    m_dot_fuel_total = calculate_fuel_mass_flow(Firepower, LHV) # fuel mass flow rate (kg/s)

    # ARGUMUENT PROCESSOR: extract the angle/flow rate definitions and create global simulation array. Fill array with
    rhs_angle_array, step_rhs, lower_angle_design_value, upper_angle_design_value = create_1d_angle_array_RHS(number_of_angles_analyzed, lower_angle_design_value, upper_angle_design_value)
    lhs_angle_array = create_1d_angle_array_LHS(rhs_angle_array, step_rhs, lower_angle_design_value, upper_angle_design_value, number_of_angles_analyzed)
    RHS_velocity_magnitude_array, LHS_velocity_magnitude_array, mass_flow_rate_array, flow_rate_RHS_empty = create_1D_velocity_magnitude_array_RHS(number_of_flowrates_analyzed, lower_flowrate_design_value, upper_flowrate_design_value, D_fd)
    N_simulations = compute_number_of_simulations(number_of_flowrates_analyzed, number_of_angles_analyzed)
    Simulation_array_empty, case_number_array_empty = create_empty_simulation_array(N_simulations)
    Global_simulation_array, Vx_RHS, Vy_RHS, Vx_LHS, Vy_LHS = fill_simulation_array(Simulation_array_empty, RHS_velocity_magnitude_array, mass_flow_rate_array, lhs_angle_array, rhs_angle_array, number_of_flowrates_analyzed, number_of_angles_analyzed, flow_rate_RHS_empty)


    # CREATE GEOMETRY AND WRITE THE MESH:
    # X-coordinate generation
    pt_49_x, pt_68_x , pt_37_x , pt_75_x , pt_30_x , pt_43_x , pt_11_x , pt_17_x , pt_55_x , pt_23_x , pt_61_x , pt_29_x , pt_67_x , pt_36_x , pt_74_x , pt_5_x , pt_42_x , pt_10_x , pt_48_x , pt_16_x , pt_54_x , pt_22_x , pt_60_x , pt_28_x , pt_66_x , pt_35_x , pt_73_x , pt_4_x, pt_41_x , pt_9_x , pt_47_x , pt_15_x , pt_53_x , pt_21_x , pt_59_x , pt_27_x , pt_65_x , pt_34_x , pt_72_x , pt_3_x , pt_40_x , pt_8_x , pt_46_x , pt_14_x , pt_52_x , pt_20_x , pt_58_x , pt_26_x , pt_64_x , pt_33_x , pt_71_x , pt_2_x , pt_39_x , pt_7_x , pt_45_x , pt_13_x , pt_51_x , pt_19_x , pt_57_x , pt_25_x , pt_63_x , pt_32_x , pt_70_x , pt_1_x , pt_38_x , pt_6_x , pt_44_x , pt_12_x , pt_50_x , pt_18_x , pt_56_x , pt_24_x , pt_62_x , pt_31_x , pt_69_x , pt_0_x = x_coordinates(stick_width, Dc, L_deck)

    # y coordinate generation
    pt_69_y , pt_32_y , pt_70_y , pt_33_y , pt_71_y , pt_34_y , pt_72_y , pt_35_y , pt_73_y , pt_36_y , pt_74_y , pt_37_y , pt_75_y , pt_62_y , pt_25_y , pt_63_y , pt_26_y , pt_64_y , pt_27_y , pt_65_y , pt_28_y , pt_66_y , pt_29_y , pt_67_y , pt_30_y , pt_68_y , pt_56_y , pt_19_y , pt_57_y , pt_20_y , pt_58_y , pt_21_y , pt_59_y , pt_22_y , pt_60_y , pt_23_y , pt_61_y , pt_18_y , pt_50_y , pt_13_y , pt_51_y , pt_14_y , pt_52_y , pt_15_y , pt_53_y , pt_16_y , pt_54_y , pt_17_y , pt_55_y , pt_12_y , pt_44_y , pt_7_y , pt_45_y , pt_8_y , pt_46_y , pt_9_y , pt_47_y , pt_10_y , pt_48_y , pt_11_y , pt_49_y , pt_6_y , pt_38_y , pt_1_y , pt_39_y , pt_2_y , pt_40_y , pt_3_y , pt_41_y , pt_4_y , pt_42_y , pt_5_y , pt_43_y , pt_0_y, pt_24_y, pt_31_y = y_coordinates(H_cc, D_fd, H_fd, stick_height, h_deck_pot)

    # z-coordinates:
    pt_0_z, pt_1_z, pt_2_z, pt_3_z, pt_4_z, pt_5_z, pt_6_z, pt_7_z, pt_8_z, pt_9_z, pt_10_z, pt_11_z, pt_12_z, pt_13_z, pt_14_z, pt_15_z, pt_16_z, pt_17_z, pt_18_z, pt_19_z, pt_20_z, pt_21_z, pt_22_z, pt_23_z, pt_24_z, pt_25_z, pt_26_z, pt_27_z, pt_28_z, pt_29_z, pt_30_z, pt_31_z, pt_32_z, pt_33_z, pt_34_z, pt_35_z, pt_36_z, pt_37_z, pt_38_z, pt_39_z, pt_40_z, pt_41_z, pt_42_z, pt_43_z, pt_44_z, pt_45_z, pt_46_z, pt_47_z, pt_48_z, pt_49_z, pt_50_z, pt_51_z, pt_52_z, pt_53_z, pt_54_z, pt_55_z, pt_56_z, pt_57_z, pt_58_z, pt_59_z, pt_60_z, pt_61_z, pt_62_z, pt_63_z, pt_64_z, pt_65_z, pt_66_z, pt_67_z , pt_68_z , pt_69_z, pt_70_z, pt_71_z, pt_72_z, pt_73_z, pt_74_z, pt_75_z = z_coordinates()

    # Convert the points to openfoam consistent strings:
    pt_0_str , pt_1_str , pt_2_str , pt_3_str , pt_4_str , pt_5_str , pt_6_str , pt_7_str , pt_8_str , pt_9_str , pt_10_str, pt_11_str, pt_12_str, pt_13_str, pt_14_str, pt_15_str, pt_16_str, pt_17_str, pt_18_str, pt_19_str, pt_20_str, pt_21_str, pt_22_str, pt_23_str, pt_24_str, pt_25_str, pt_26_str, pt_27_str, pt_28_str, pt_29_str, pt_30_str, pt_31_str, pt_32_str, pt_33_str, pt_34_str, pt_35_str, pt_36_str, pt_37_str, pt_38_str, pt_39_str, pt_40_str, pt_41_str, pt_42_str, pt_43_str, pt_44_str, pt_45_str, pt_46_str, pt_47_str, pt_48_str, pt_49_str, pt_50_str, pt_51_str, pt_52_str, pt_53_str, pt_54_str, pt_55_str, pt_56_str, pt_57_str, pt_58_str, pt_59_str, pt_60_str, pt_61_str, pt_62_str, pt_63_str, pt_64_str, pt_65_str, pt_66_str, pt_67_str, pt_68_str, pt_69_str, pt_70_str, pt_71_str, pt_72_str, pt_73_str, pt_74_str, pt_75_str =create_coordinate_strings(pt_49_x, pt_68_x , pt_37_x , pt_75_x , pt_30_x , pt_43_x , pt_11_x , pt_17_x , pt_55_x , pt_23_x , pt_61_x , pt_29_x , pt_67_x , pt_36_x , pt_74_x , pt_5_x , pt_42_x , pt_10_x , pt_48_x , pt_16_x , pt_54_x , pt_22_x , pt_60_x , pt_28_x , pt_66_x , pt_35_x , pt_73_x , pt_4_x, pt_41_x , pt_9_x , pt_47_x , pt_15_x , pt_53_x , pt_21_x , pt_59_x , pt_27_x , pt_65_x , pt_34_x , pt_72_x , pt_3_x , pt_40_x , pt_8_x , pt_46_x , pt_14_x , pt_52_x , pt_20_x , pt_58_x , pt_26_x , pt_64_x , pt_33_x , pt_71_x , pt_2_x , pt_39_x , pt_7_x , pt_45_x , pt_13_x , pt_51_x , pt_19_x , pt_57_x , pt_25_x , pt_63_x , pt_32_x , pt_70_x , pt_1_x , pt_38_x , pt_6_x , pt_44_x , pt_12_x , pt_50_x , pt_18_x , pt_56_x , pt_24_x , pt_62_x , pt_31_x , pt_69_x , pt_0_x, pt_0_z, pt_1_z, pt_2_z, pt_3_z, pt_4_z, pt_5_z, pt_6_z, pt_7_z, pt_8_z, pt_9_z, pt_10_z, pt_11_z, pt_12_z, pt_13_z, pt_14_z, pt_15_z, pt_16_z, pt_17_z, pt_18_z, pt_19_z, pt_20_z, pt_21_z, pt_22_z, pt_23_z, pt_24_z, pt_25_z, pt_26_z, pt_27_z, pt_28_z, pt_29_z, pt_30_z, pt_31_z, pt_32_z, pt_33_z, pt_34_z, pt_35_z, pt_36_z, pt_37_z, pt_38_z, pt_39_z, pt_40_z, pt_41_z, pt_42_z, pt_43_z, pt_44_z, pt_45_z, pt_46_z, pt_47_z, pt_48_z, pt_49_z, pt_50_z, pt_51_z, pt_52_z, pt_53_z, pt_54_z, pt_55_z, pt_56_z, pt_57_z, pt_58_z, pt_59_z, pt_60_z, pt_61_z, pt_62_z, pt_63_z, pt_64_z, pt_65_z, pt_66_z, pt_67_z , pt_68_z , pt_69_z, pt_70_z, pt_71_z, pt_72_z, pt_73_z, pt_74_z, pt_75_z,  pt_69_y , pt_32_y , pt_70_y , pt_33_y , pt_71_y , pt_34_y , pt_72_y , pt_35_y , pt_73_y , pt_36_y , pt_74_y , pt_37_y , pt_75_y , pt_62_y , pt_25_y , pt_63_y , pt_26_y , pt_64_y , pt_27_y , pt_65_y , pt_28_y , pt_66_y , pt_29_y , pt_67_y , pt_30_y , pt_68_y , pt_56_y , pt_19_y , pt_57_y , pt_20_y , pt_58_y , pt_21_y , pt_59_y , pt_22_y , pt_60_y , pt_23_y , pt_61_y , pt_18_y , pt_50_y , pt_13_y , pt_51_y , pt_14_y , pt_52_y , pt_15_y , pt_53_y , pt_16_y , pt_54_y , pt_17_y , pt_55_y , pt_12_y , pt_44_y , pt_7_y , pt_45_y , pt_8_y , pt_46_y , pt_9_y , pt_47_y , pt_10_y , pt_48_y , pt_11_y , pt_49_y , pt_6_y , pt_38_y , pt_1_y , pt_39_y , pt_2_y , pt_40_y , pt_3_y , pt_41_y , pt_4_y , pt_42_y , pt_5_y , pt_43_y , pt_0_y, pt_24_y, pt_31_y)

    # Mesh writing:
    current_dir = determine_working_directory()
    block_mesh_template = find_block_mesh_template(current_dir)


    write_mesh_0422(block_mesh_template, pt_0_str , pt_1_str , pt_2_str , pt_3_str , pt_4_str , pt_5_str , pt_6_str , pt_7_str , pt_8_str , pt_9_str , pt_10_str, pt_11_str, pt_12_str, pt_13_str, pt_14_str, pt_15_str, pt_16_str, pt_17_str, pt_18_str, pt_19_str, pt_20_str, pt_21_str, pt_22_str, pt_23_str, pt_24_str, pt_25_str, pt_26_str, pt_27_str, pt_28_str, pt_29_str, pt_30_str, pt_31_str, pt_32_str, pt_33_str, pt_34_str, pt_35_str, pt_36_str, pt_37_str, pt_38_str, pt_39_str, pt_40_str, pt_41_str, pt_42_str, pt_43_str, pt_44_str, pt_45_str, pt_46_str, pt_47_str, pt_48_str, pt_49_str, pt_50_str, pt_51_str, pt_52_str, pt_53_str, pt_54_str, pt_55_str, pt_56_str, pt_57_str, pt_58_str, pt_59_str, pt_60_str, pt_61_str, pt_62_str, pt_63_str, pt_64_str, pt_65_str, pt_66_str, pt_67_str, pt_68_str, pt_69_str, pt_70_str, pt_71_str, pt_72_str, pt_73_str, pt_74_str, pt_75_str)


    """
    # case_setup mod
    simulation_folder_path = create_simulations_folder()
    case_number_array, case_path_array = create_case_directories(N_simulations, simulation_folder_path)
    case_zero_paths, case_system_paths, case_constant_paths, case_TDAC_paths = add_foam_directories(case_path_array, N_simulations)
    paste_static_foam_files(case_zero_paths, case_system_paths, case_constant_paths, case_TDAC_paths, N_simulations)

    """
    # Create X number of results matrices: col 1 is case number, col 2 is the secondary flow rate, col 3 is the secondary angle, col 4 is the respective dependent variable being tracked


    # Create a geometry and mesh --> pull this entirely from the previous work, woohoo!


    # loop through the simulations, pull data from the post processing of the case, place values iteratively in the CORRECT results matrix col 4


    # plot results in matlplotlib



    # Ensure the args all work-->string vs non string, slash variations, quotation marks
    #correct_arguments(args)
    print('args printed:')
    print(args)

if __name__ == "__main__":
    main()
