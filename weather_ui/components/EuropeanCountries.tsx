"use client";

import * as React from "react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

export const EUROPEAN_COUNTRIES = [
    "Amsterdam",
    "Andorra la Vella",
    "Athens",
    "Belgrade",
    "Berlin",
    "Bern",
    "Bratislava",
    "Brussels",
    "Bucharest",
    "Budapest",
    "Chisinau",
    "Copenhagen",
    "Dublin",
    "Helsinki",
    "Kyiv",
    "Lisbon",
    "Ljubljana",
    "London",
    "Luxembourg",
    "Madrid",
    "Minsk",
    "Monaco",
    "Moscow",
    "Oslo",
    "Paris",
    "Rome",
    "Vatican City",
    "Vienna",
    "Zug Spitz",
    "Sermersooq"
];

type Props = {
    value?: string;
    onChange: (value: string) => void;
    placeholder?: string;
};

export default function EuropeanCountrySelect({ value, onChange, placeholder = "Select a country" }: Props) {
    return (
        <Select value={value} onValueChange={onChange}>
            <SelectTrigger className="w-full">
                <SelectValue placeholder={placeholder} />
            </SelectTrigger>

            <SelectContent className="max-h-72">
                {EUROPEAN_COUNTRIES.map((country) => (
                    <SelectItem key={country} value={country}>
                        {country}
                    </SelectItem>
                ))}
            </SelectContent>
        </Select>
    );
}
