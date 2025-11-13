import pandas as pd

def prepare_dataset(path_csv: str, sample_fraction: float = 0.1) -> pd.DataFrame:
  
    #Le o CSV
    df = pd.read_csv(path_csv)
    #Fraciona o dataset se necessário
    df = df.sample(frac=sample_fraction, random_state=42)
    #colunas relevantes
    cols = [
        "Product ID", "Category", "Inventory Level", "Units Sold",
        "Demand Forecast", "Price", "Competitor Pricing"
    ]
    df = df[cols].copy()

   
    df_grouped = df.groupby(["Product ID", "Category"], as_index=False).agg({
        "Inventory Level": "mean",
        "Units Sold": "sum",
        "Demand Forecast": "mean",
        "Price": "mean",
        "Competitor Pricing": "mean"
    })

    df_grouped["Lucro Estimado"] = (
        (df_grouped["Price"] - df_grouped["Competitor Pricing"]) * df_grouped["Demand Forecast"]
    ).clip(lower=0)

    df_grouped["Volume (m³)"] = df_grouped["Inventory Level"]

    df_grouped["Giro de Estoque"] = (
        df_grouped["Units Sold"] / (df_grouped["Inventory Level"] + 1e-9)
    )

    
    df_grouped["Volume (m³)"] = (
        df_grouped["Volume (m³)"] / df_grouped["Volume (m³)"].max() * 100
    )


    final_df = df_grouped[[
        "Product ID", "Category", "Lucro Estimado", "Volume (m³)", "Giro de Estoque"
    ]]

    print(f"\n Dataset preparado com {len(final_df)} produtos únicos.\n")
    print(final_df.head(10))

    return final_df