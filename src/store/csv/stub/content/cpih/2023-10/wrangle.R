library(dplyr)
library(lubridate)
library(readr)
library(stringr)


df <- read_csv("https://www.ons.gov.uk/generator?format=csv&uri=/economy/inflationandpriceindices/timeseries/l55o/mm23")

df <- df[-(1:7), ] |>
    rename(date = Title, cpih_annual_rate = `CPIH ANNUAL RATE 00: ALL ITEMS 2015=100`) |>
    mutate(geography = "K02000001", geography_name = "United Kingdom", .before = everything()) |>
    mutate(date = case_when(
        str_detect(date, "^\\d{4}$") ~ date,
        str_detect(date, "^\\d{4} [A-Z]{3}$") ~ ym(date, quiet = TRUE) |> format("%Y-%m"),
        str_detect(date, "^\\d{4} Q[1-4]$") ~ str_replace_all(date, " ", "-"),
        TRUE ~ NA
    ))

write_csv(df, "src/store/csv/stub/content/cpih/2023-10/1.csv")
