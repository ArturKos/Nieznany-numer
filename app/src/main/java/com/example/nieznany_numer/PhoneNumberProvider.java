package com.example.nieznany_numer;

import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;

import java.io.IOException;

public class PhoneNumberProvider {
    public void getPhoneNumberInfo(String Phone_number) {
        new Thread(new Runnable() {
            @Override
            public void run() {
                final StringBuilder builder = new StringBuilder();

                try {
                    String url = "https://www.nieznany-numer.pl/Numer/" + Phone_number;
                    Document doc = Jsoup.connect(url).get();
                    Elements data_divs = doc.select("div.dataColumn");
                    Integer index = 0;
                    String[] strings = {"Ocena: ", "Wyszukiwań: ", "Komentarzy: ", "Ostatnio sprawdzany: "};

                    for (Element data : data_divs) {
                        if (index <= 3)
                            builder.append("\n").append(strings[index++]).append(data.text());
                    }
                } catch (IOException e) {
                    builder.append("Error : ").append(e.getMessage()).append("\n");
                }

                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        MainActivity.result.setText(builder.toString());
                    }
                });
            }
        }).start();
    }
}
