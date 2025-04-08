import logging

# Air properties in 20ºC due to https://calcdevice.com/natural-convection-of-vertical-surface-id128.html
fluid_thermal_conductivity = 0.0259  # W/m*ºC
dynamic_viscosity = 0.000018  # Pa*s
fluid_specific_heat = 1005  # J/kg*⁰C
volumetric_expansion = 0.00365  # 1/⁰C
density = 1.205  # kg/m³
gravity = 9.80665  # m/s^2
# Nusselt number coefficients for natural convection of
# top horizontal plane due to https://volupe.com/support/empirical-correlations-for-convective-heat-transfer-coefficients/
n = 0.25
c = 0.54


def calculate_film_coefficient(
    temp_fluid: float, temp_surface: float, orientation: str, length: float
):
    # Characteristic length [mm]
    length = length / 1000

    if orientation == "vertical":
        orientation_multiplier: float = 1
        # c = 0.68
    elif orientation == "horizontal_up":
        orientation_multiplier = 1.3
        # c = 0.54
    elif orientation == "horizontal_down":
        orientation_multiplier = 0.7
        # c = 0.27

    # fmt: off
    grashof_number = (
        gravity * pow(length, 3) * volumetric_expansion * (temp_surface - temp_fluid)
        / pow((dynamic_viscosity / density), 2)
    )
    prandtl_number = dynamic_viscosity * fluid_specific_heat / fluid_thermal_conductivity
    rayleigh_number = grashof_number * prandtl_number
    nusselt_number = c * pow(rayleigh_number, n)
    film_coefficient = orientation_multiplier * nusselt_number * fluid_thermal_conductivity / length
    # fmt: on

    logging.debug(f"Grashof_number = {grashof_number}")
    logging.debug(f"Prandtl_number = {prandtl_number}")
    logging.debug(f"Rayleigh_number = {rayleigh_number}")
    logging.debug(f"Nusselt_number = {nusselt_number}")
    logging.debug(f"Film coefficient = {film_coefficient}")
    # heat_flow = film_coefficient * (temp_surface-temp_fluid)
    # transmitted_power = film_coefficient*width*length*(temp_surface-temp_fluid)
    # logging.debug(f"Heat flow = {heat_flow}")
    # logging.debug(f"Transmitted power = {transmitted_power}")
    return film_coefficient
