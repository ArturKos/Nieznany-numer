package com.example.nieznany_numer;

import android.content.Context;
import android.graphics.Color;

import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;
import java.io.IOException;


public class PhoneNumberProvider {

    public void getPhoneNumberInfo(Context context,String Phone_number) {
        new Thread(new Runnable() {
            @Override
            public void run() {
                final StringBuilder builder = new StringBuilder();
                String ocena="";
                try {
                    String url = "https://www.nieznany-numer.pl/Numer/" + Phone_number;

                    Document doc = Jsoup.connect(url).get();
                    Elements data_divs = doc.select("div.dataColumn");
                    builder.append("\n").append(context.getString(R.string.telephone_ringing) + Phone_number);
                    Integer index = 0;
                    String[] strings = {context.getString(R.string.telephone_ocena),
                                        context.getString(R.string.telephone_searches),
                                        context.getString(R.string.telephone_comments),
                                        context.getString(R.string.telephone_last_checked)};

                    for (Element data : data_divs) {
                        if (index <= 3) {
                            if(index == 0) ocena = data.text();
                            builder.append("\n").append(strings[index++]).append(data.text());
                        }
                    }
                } catch (IOException e) {
                    builder.append(context.getString(R.string.error_geting_pn_info)).append(e.getMessage()).append("\n");
                }
                switch(ocena)
                { //TODO change stings to english
                    case "Negatywna": MainActivity.result.setTextColor(Color.RED); break;
                    case "Neutralna": MainActivity.result.setTextColor(Color.GREEN); break;
                }
                MainActivity.setTextViewText(builder.toString());
            }
        }).start();
    }
}