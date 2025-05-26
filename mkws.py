import cantera as ct
import numpy as np
import matplotlib.pyplot as plt
from sdtoolbox.postshock import CJspeed

# Mieszanki paliwowo-utleniające
mixtures = {
    '1': ('H2', 'O2'),
    '2': ('CH4', 'O2'),
    '3': ('C2H2', 'O2'),
    '4': ('H2', 'air'),
    '5': ('CH4', 'air')
}

def select_mixture():
    print("Wybierz mieszaninę paliwowo-utleniającą:")
    for key, (fuel, oxidizer) in mixtures.items():
        print(f"{key}: {fuel} + {oxidizer}")
    choice = input("Podaj numer mieszanki (1-5): ").strip()
    return mixtures.get(choice, ('H2', 'O2'))

def get_user_input():
    fuel, oxidizer = select_mixture()
    print(f"Wybrano mieszankę: {fuel} + {oxidizer}")

    try:
        phi = float(input("Podaj stosunek stechiometryczny (ϕ), np. 1.0: "))
        T0 = float(input("Podaj temperaturę początkową [K], np. 300: "))
        P0 = float(input("Podaj ciśnienie początkowe [Pa], np. 101325: "))
        V0 = float(input("Podaj objętość początkową [m³], np. 1.0: "))
    except ValueError:
        print("Nieprawidłowe dane. Używam wartości domyślnych.")
        phi, T0, P0, V0 = 1.0, 300.0, 101325.0, 1.0

    return fuel, oxidizer, phi, T0, P0, V0

def calculate_cj_speed(p, T, q, mech):
    gas = ct.Solution(mech)
    gas.TPX = T, p, q
    return CJspeed(p, T, q, mech)

def calculate_results(fuel, oxidizer, phi, T0, P0, V0):
    gas = ct.Solution('gri30.yaml')
    gas.set_equivalence_ratio(phi, fuel, oxidizer)
    gas.TP = T0, P0
    gas.equilibrate('UV')

    T_final = gas.T
    P_final = gas.P
    rho_final = gas.density
    a_final = gas.sound_speed
    composition_final = gas.X

    q = f"{fuel}:{phi} {oxidizer}:{phi}"
    cj_speed = calculate_cj_speed(P0, T0, q, 'gri30.yaml')

    print("\n--- WYNIKI (spalanie w stałej objętości) ---")
    print(f"Temperatura końcowa: {T_final:.2f} K")
    print(f"Ciśnienie końcowe: {P_final/1e5:.2f} bar")
    print(f"Gęstość: {rho_final:.2f} kg/m³")
    print(f"Prędkość dźwięku: {a_final:.2f} m/s")
    print(f"Prędkość detonacji CJ: {cj_speed:.2f} m/s")
    print("Skład końcowy (wybrane składniki):")
    for species in ['H2', 'H', 'O', 'OH', 'H2O', 'C', 'CH', 'CO', 'CO2']:
        if species in gas.species_names:
            idx = gas.species_names.index(species)
            print(f"  {species}: {composition_final[idx]:.4f}")

def generate_plots(fuel, oxidizer, T0, P0):
    phi_range = np.linspace(0.5, 2.0, 30)
    T_list, P_list, rho_list = [], [], []
    CO_list, CO2_list, H2O_list, OH_list = [], [], [], []

    gas = ct.Solution('gri30.yaml')

    for phi in phi_range:
        gas.set_equivalence_ratio(phi, fuel, oxidizer)
        gas.TP = T0, P0
        gas.equilibrate('UV')

        T_list.append(gas.T)
        P_list.append(gas.P / 1e5)
        rho_list.append(gas.density)

        species_names = gas.species_names
        X = gas.X

        CO_list.append(X[species_names.index('CO')] if 'CO' in species_names else 0)
        CO2_list.append(X[species_names.index('CO2')] if 'CO2' in species_names else 0)
        H2O_list.append(X[species_names.index('H2O')] if 'H2O' in species_names else 0)
        OH_list.append(X[species_names.index('OH')] if 'OH' in species_names else 0)

    # Wykresy
    plt.figure(figsize=(10, 6))
    plt.plot(phi_range, T_list, label='Temperatura [K]')
    plt.title('Temperatura końcowa vs. stosunek stechiometryczny (ϕ)')
    plt.xlabel('ϕ')
    plt.ylabel('Temperatura [K]')
    plt.grid()
    plt.legend()
    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(10, 6))
    plt.plot(phi_range, P_list, label='Ciśnienie [bar]', color='orange')
    plt.title('Ciśnienie końcowe vs. stosunek stechiometryczny (ϕ)')
    plt.xlabel('ϕ')
    plt.ylabel('Ciśnienie [bar]')
    plt.grid()
    plt.legend()
    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(10, 6))
    plt.plot(phi_range, rho_list, label='Gęstość [kg/m³]', color='green')
    plt.title('Gęstość końcowa vs. stosunek stechiometryczny (ϕ)')
    plt.xlabel('ϕ')
    plt.ylabel('Gęstość [kg/m³]')
    plt.grid()
    plt.legend()
    plt.tight_layout()
    plt.show()

    # Składniki spalin
    plt.figure(figsize=(10, 6))
    plt.plot(phi_range, CO_list, label='CO')
    plt.plot(phi_range, CO2_list, label='CO₂')
    plt.plot(phi_range, H2O_list, label='H₂O')
    plt.plot(phi_range, OH_list, label='OH')
    plt.title('Wybrane składniki spalin vs. stosunek stechiometryczny (ϕ)')
    plt.xlabel('ϕ')
    plt.ylabel('Ułamek molowy')
    plt.grid()
    plt.legend()
    plt.tight_layout()
    plt.show()

# Główna funkcja
if __name__ == "__main__":
    fuel, oxidizer, phi, T0, P0, V0 = get_user_input()
    calculate_results(fuel, oxidizer, phi, T0, P0, V0)
    generate_plots(fuel, oxidizer, T0, P0)
