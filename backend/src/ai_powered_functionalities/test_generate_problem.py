import asyncio
from backend.src.ai_powered_functionalities.generate_problem_statements.generate_problems import GenerateProblem


async def test_generation():
    generator = GenerateProblem()

    print("Generating problem...")
    result = await generator.generate_problem()

    print("\n" + "=" * 50)
    print("GENERATED PROBLEM:")
    print("=" * 50)
    print(f"\nEnunț:\n{result.enunt}")
    print(f"\nDate de intrare:\n{result.date_intrare}")
    print(f"\nDate de ieșire:\n{result.date_iesire}")
    print(f"\nExemplu intrare:\n{result.exemplu_intrare}")
    print(f"\nExemplu ieșire:\n{result.exemplu_iesire}")
    print(f"\nDificultate: {result.nivel_dificultate}")


if __name__ == "__main__":
    asyncio.run(test_generation())