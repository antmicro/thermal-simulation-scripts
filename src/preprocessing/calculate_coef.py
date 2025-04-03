#Air properties in 20ºC
fluid_thermal_conductivity = 0.026 #W/m*ºC
dynamic_viscosity = 0.0000182 # Pa*s
fluid_specific_heat = 1004.5  # J/kg*⁰C
volumetric_expansion = 0.00343 # 1/⁰C
density = 1.204 # kg/m³
gravity = 9.80665 # m/s^2
n=0.25
c=0.54

def calculate_film_coefficient(temp_fluid:float, temp_surface:float, orientation:str, length:float):

    # width = width/1000
    length = length/1000 # Characteristic length

    if orientation == 'vertical':
        orientation_multiplier=1
    elif orientation == 'horizontal_up':
        orientation_multiplier=1.3
    elif orientation == 'horizontal_down':        
        orientation_multiplier=0.7

    grashof_number = gravity * pow(length,3) *  volumetric_expansion * (temp_surface - temp_fluid) / pow((dynamic_viscosity/density),2)
    prandtl_number = dynamic_viscosity*fluid_specific_heat/fluid_thermal_conductivity
    rayleigh_number = grashof_number * prandtl_number
    nusselt_number = c * pow(rayleigh_number,n) 
    film_coefficient = orientation_multiplier * nusselt_number * fluid_thermal_conductivity/length
    heat_flow = film_coefficient * (temp_surface-temp_fluid)
    # transmitted_power = film_coefficient*width*length*(temp_surface-temp_fluid)

    print(f"Grashof_number = {grashof_number}")
    print(f"Prandtl_number = {prandtl_number}")
    print(f"Rayleigh_number = {rayleigh_number}")
    print(f"Nusselt_number = {nusselt_number}")
    print(f"Film coefficient = {film_coefficient}")
    print(f"Heat flow = {heat_flow}")
    # print(f"Transmitted power = {transmitted_power}")

    return film_coefficient

