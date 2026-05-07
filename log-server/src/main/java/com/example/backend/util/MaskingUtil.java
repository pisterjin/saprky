package com.example.backend.util;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class MaskingUtil {

    public record MaskingResult(String masked, boolean hit) {}

    private static final Pattern RRN    = Pattern.compile("\\b(\\d{6})-([1-4]\\d{6})\\b");
    private static final Pattern CARD   = Pattern.compile("\\b(\\d{4})[-.\\s](\\d{4})[-.\\s](\\d{4})[-.\\s](\\d{4})\\b");
    private static final Pattern PHONE  = Pattern.compile("\\b(01[016789])[-.\\s]?(\\d{3,4})[-.\\s]?(\\d{4})\\b");
    private static final Pattern ACCT   = Pattern.compile("(?:계좌|account|acnt)\\s*[번호:：]?\\s*(\\d[\\d\\-]{9,17})");
    private static final Pattern EMAIL  = Pattern.compile("\\b[A-Za-z0-9._%+\\-]+@[A-Za-z0-9.\\-]+\\.[A-Za-z]{2,}\\b");

    public static MaskingResult mask(String text) {
        if (text == null || text.isEmpty()) return new MaskingResult(text, false);

        boolean hit = false;
        String result = text;

        // R1: 주민등록번호
        Matcher m1 = RRN.matcher(result);
        if (m1.find()) { hit = true; result = m1.replaceAll("######-*******"); }

        // R2: 카드번호
        Matcher m2 = CARD.matcher(result);
        if (m2.find()) { hit = true; result = m2.replaceAll("****-****-****-****"); }

        // R3: 휴대폰
        StringBuffer sb3 = new StringBuffer();
        Matcher m3 = PHONE.matcher(result);
        boolean phone_hit = false;
        while (m3.find()) { phone_hit = true; m3.appendReplacement(sb3, m3.group(1) + "-****-****"); }
        if (phone_hit) { hit = true; m3.appendTail(sb3); result = sb3.toString(); }

        // R4: 계좌번호
        StringBuffer sb4 = new StringBuffer();
        Matcher m4 = ACCT.matcher(result);
        boolean acct_hit = false;
        while (m4.find()) {
            acct_hit = true;
            String full = m4.group(0);
            String num  = m4.group(1);
            m4.appendReplacement(sb4, Matcher.quoteReplacement(full.replace(num, "[계좌번호]")));
        }
        if (acct_hit) { hit = true; m4.appendTail(sb4); result = sb4.toString(); }

        // R5: 이메일
        Matcher m5 = EMAIL.matcher(result);
        if (m5.find()) { hit = true; result = m5.replaceAll("[이메일]"); }

        return new MaskingResult(result, hit);
    }

    public static String maskText(String text) {
        return mask(text).masked();
    }
}
