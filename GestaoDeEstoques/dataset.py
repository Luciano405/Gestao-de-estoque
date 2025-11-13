import pandas as pd

def prepare_dataset(path_csv: str, sample_fraction: float = 0.1) -> pd.DataFrame:

    """
    Prepara o dataset para o algoritmo Branch & Bound:

    """

    
    df = pd.read_csv(path_csv)

    df = df.sample(frac=sample_fraction, random_state=42)

    cols = [
        "Product ID", "Category", "Inventory Level", "Units Sold",
        "Demand Forecast", "Price"
    ]
    df = df[cols].copy()

    df_grouped = df.groupby(["Product ID", "Category"], as_index=False).agg({
        "Inventory Level": "mean",
        "Units Sold": "sum",
        "Demand Forecast": "mean",
        "Price": "mean"
    })

    df_grouped["Lucro Estimado"] = (
        df_grouped["Price"] * 0.30 * df_grouped["Demand Forecast"]
    )

    df_grouped["Volume (m³)"] = df_grouped["Inventory Level"]


    df_grouped["Volume (m³)"] = (
        df_grouped["Volume (m³)"] / df_grouped["Volume (m³)"].max() * 100
    )


    df_grouped["Giro de Estoque"] = (
        df_grouped["Units Sold"] / (df_grouped["Inventory Level"] + 1e-9)
    )

 
    final_df = df_grouped[[
        "Product ID", "Category", "Lucro Estimado", "Volume (m³)", "Giro de Estoque"
    ]]


    final_df = final_df.round(2)


    print(f"\n Dataset preparado com {len(final_df)} produtos únicos.\n")
    print(final_df.head(10))

    return final_df
