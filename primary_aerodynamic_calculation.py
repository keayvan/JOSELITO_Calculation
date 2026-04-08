# -*- coding: utf-8 -*-
"""
Created on Wed Apr  8 10:11:21 2026

@author: kkeramati
"""

import math
import numpy as np
from dataclasses import dataclass
from matplotlib import pyplot as plt

@dataclass 
class Request_config:
    mass_kg:float = 5.0                   # total drone mass
    speed_kmh:float = 300               # target cruise speed
    flight_time_min:float = 5.0          # desired flight time
    
@dataclass 
class Drone_config:
    rho:float = 1.225                     # air density at sea level [kg/m^3]
    Cd:float = 0.25                       # drag coefficient (optimistic streamlined body)
    A_front:float = 0.0176                # frontal area [m^2]
    Cl:float = 0.50     
@dataclass 
class Battery_config:
    eta_total:float = 0.70                # total efficiency (motor + ESC + propulsive)
    battery_cells:float = 6              # 12S, 14S, etc.
    cell_nominal_voltage:float = 3.7      # LiPo nominal voltage per cell
    usable_fraction:float = 0.80          # use only 80% of pack
    battery_specific_energy:float = 180   # Wh/kg, rough practical estimate
        
    
def drag_force(rho, V, Cd, A_front):
    """
    Drag force:
    D = 0.5 * rho * V^2 * Cd * A
    """
    return 0.5 * rho * V**2 * Cd * A_front


def lift_force(rho, V, Cl, S):
    """
    Lift force:
    L = 0.5 * rho * V^2 * Cl * S
    """
    return 0.5 * rho * V**2 * Cl * S


def required_wing_area_for_level_flight(mass, rho, V, Cl):
    """
    Solve lift equation for wing/reference area S:
    mg = 0.5 * rho * V^2 * Cl * S
    """
    weight = mass * 9.81
    return weight / (0.5 * rho * V**2 * Cl)


def mechanical_power_from_drag(D, V):
    """
    Cruise mechanical power:
    P_mech = D * V
    """
    return D * V


def electrical_power_required(P_mech, eta_total):
    """
    Electrical power needed from battery:
    P_elec = P_mech / eta_total
    """
    if eta_total <= 0 or eta_total > 1:
        raise ValueError("eta_total must be between 0 and 1.")
    return P_mech / eta_total


def battery_energy_wh(P_elec, flight_time_min):
    """
    Battery energy in Wh:
    E = P * t
    with t in hours
    """
    t_hours = flight_time_min / 60.0
    return P_elec * t_hours


def required_battery_capacity_ah(E_wh, V_bat_nominal, usable_fraction=0.8):
    """
    Required battery capacity in Ah.
    We divide by usable_fraction because you normally do not use 100% of battery.
    """
    if usable_fraction <= 0 or usable_fraction > 1:
        raise ValueError("usable_fraction must be between 0 and 1.")
    return E_wh / (V_bat_nominal * usable_fraction)


def battery_current(P_elec, V_bat_nominal):
    """
    Battery current:
    I = P / V
    """
    return P_elec / V_bat_nominal


def required_c_rating(I_required, capacity_ah):
    """
    Minimum C rating:
    C = I / Ah
    """
    return I_required / capacity_ah


def battery_mass_from_energy(E_wh, specific_energy_wh_per_kg=180, usable_fraction=0.8):
    """
    Estimate battery mass from required stored energy.
    If only 80% is usable, total stored energy must be larger.
    """
    total_stored_energy = E_wh / usable_fraction
    return total_stored_energy / specific_energy_wh_per_kg


def kmh_to_ms(speed_kmh):
    return speed_kmh / 3.6


def print_results(title, value, unit=""):
    if isinstance(value, float):
        print(f"{title:<35}: {value:,.3f} {unit}")
    else:
        print(f"{title:<35}: {value} {unit}")


if __name__ == "__main__":
    plt.rcParams["font.family"] = "Century Gothic"

    # ==========================================================
    # INPUTS — CHANGE THESE FOR YOUR DRONE
    # ==========================================================
    Request_config = Request_config(
                mass_kg = 5.0,                   # total drone mass
                speed_kmh = 300,               # target cruise speed
                flight_time_min = 5.0,         # desired flight time
                    )
    Drone_config = Drone_config(
                rho = 1.225,                     # air density at sea level [kg/m^3]
                Cd = 0.25,                       # drag coefficient (optimistic streamlined body)
                A_front = 0.024,                # frontal area [m^2]
                Cl = 0.50
                    )
        
    Battery_config = Battery_config(
                eta_total = 0.70,                # total efficiency (motor + ESC + propulsive)
                battery_cells = 6,               # 12S, 14S, etc.
                cell_nominal_voltage = 3.7,      # LiPo nominal voltage per cell
                usable_fraction = 0.95,          # use only 80% of pack
                battery_specific_energy = 180
                    )
        
    mass_kg = Request_config.mass_kg
    speed_kmh = Request_config.speed_kmh               # target cruise speed
    flight_time_min = Request_config.flight_time_min        # desired flight time

    rho = Drone_config.rho                    # air density at sea level [kg/m^3]
    Cd = Drone_config.Cd                       # drag coefficient (optimistic streamlined body)
    A_front = Drone_config.A_front                # frontal area [m^2]
    Cl = Drone_config.Cl                       # lift coefficient if using wing

    eta_total = Battery_config.eta_total                # total efficiency (motor + ESC + propulsive)
    battery_cells = Battery_config.battery_cells             # 12S, 14S, etc.
    cell_nominal_voltage = Battery_config.cell_nominal_voltage      # LiPo nominal voltage per cell
    usable_fraction =Battery_config.usable_fraction         # use only 80% of pack
    battery_specific_energy = Battery_config.battery_specific_energy   # Wh/kg, rough practical estimate

    # ==========================================================
    # DERIVED VALUES
    # ==========================================================
    V = kmh_to_ms(speed_kmh)
    weight = mass_kg * 9.81
    V_bat_nominal = battery_cells * cell_nominal_voltage

    # ==========================================================
    # AERODYNAMICS
    # ==========================================================
    D = drag_force(rho, V, Cd, A_front)
    P_mech = mechanical_power_from_drag(D, V)
    P_elec = electrical_power_required(P_mech, eta_total)

    # If you want wing area needed for level flight at this speed:
    S_required = required_wing_area_for_level_flight(mass_kg, rho, V, Cl)

    # Check resulting lift for that area
    L_check = lift_force(rho, V, Cl, S_required)

    # ==========================================================
    # BATTERY
    # ==========================================================
    E_wh = battery_energy_wh(P_elec, flight_time_min)
    capacity_ah = required_battery_capacity_ah(E_wh, V_bat_nominal, usable_fraction)
    I_cruise = battery_current(P_elec, V_bat_nominal)
    C_min = required_c_rating(I_cruise, capacity_ah)
    battery_mass = battery_mass_from_energy(E_wh, battery_specific_energy, usable_fraction)

    # ==========================================================
    # OUTPUTS
    # ==========================================================
    print("\n========== DRONE PRELIMINARY DESIGN CALCULATOR ==========\n")

    print("---- INPUTS ----")
    print_results("Mass", mass_kg, "kg")
    print_results("Speed", speed_kmh, "km/h")
    print_results("Speed", V, "m/s")
    print_results("Flight time", flight_time_min, "min")
    print_results("Air density", rho, "kg/m^3")
    print_results("Drag coefficient Cd", Cd, "")
    print_results("Frontal area", A_front, "m^2")
    print_results("Lift coefficient Cl", Cl, "")
    print_results("Total efficiency", eta_total, "")
    print_results("Battery", f"{battery_cells}S", "")
    print_results("Battery nominal voltage", V_bat_nominal, "V")

    print("\n---- AERODYNAMICS ----")
    print_results("Weight", weight, "N")
    print_results("Drag force (min forward thrust)", D, "N")
    print_results("Take off thrust", weight*1.5, "N")

    
    print_results("Mechanical cruise power", P_mech, "W")
    print_results("Electrical cruise power", P_elec, "W")
    print_results("Required wing area", S_required, "m^2")
    print_results("Lift check", L_check, "N")

    print("\n---- BATTERY ----")
    print_results("Energy needed", E_wh, "Wh")
    print_results("Required battery capacity", capacity_ah, "Ah")
    print_results("Cruise current", I_cruise, "A")
    print_results("Minimum C-rating (cruise only)", C_min, "C")
    print_results("Estimated battery mass", battery_mass, "kg")

    print("\n---- NOTES ----")
    print("* Cruise-only sizing is optimistic.")
    print("* Real design must also include takeoff, climb, transition, peak current, and reserve.")
    print("* For a VTOL/pusher concept, actual required battery may be significantly larger.")
    
    #===========================================
    #battery weight vs speed
    speed = np.linspace(200, 600, 20)
    weight_all = []
    for i, v in enumerate (speed):
        V = kmh_to_ms(v)
        weight = mass_kg * 9.81

        D = drag_force(rho, V, Cd, A_front)
        P_mech = mechanical_power_from_drag(D, V)
        P_elec = electrical_power_required(P_mech, eta_total)
        E_wh = battery_energy_wh(P_elec, flight_time_min)
        battery_mass = battery_mass_from_energy(E_wh, battery_specific_energy, usable_fraction)
        weight_all.append(battery_mass)

    fig, ax = plt.subplots (1 ,2)
    ax = ax.ravel()
    ax[0].plot(speed, weight_all, '-o')
    ax[0].grid("both")
    ax[0].set_xlabel("Speed (Km/h)")
    ax[0].set_ylabel("battery weight (Kg)")
    
    front_area = np.linspace(0.008, 0.022, 20)
    
    D_all = []
    for i,v in enumerate(front_area):
        D = drag_force(rho, V, Cd, v)
        D_all.append(D)
        
    ax[1].plot(front_area, D_all, '-o')
    ax[1].grid("both")
    ax[1].set_xlabel("Front area m2")
    ax[1].set_ylabel("Requiered thrust @cruise speed (N)")
        
    
    