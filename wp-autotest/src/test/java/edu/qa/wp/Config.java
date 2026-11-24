package edu.qa.wp;

/** 全局配置：被测地址与各角色账号 */
public final class Config {

    public static final String BASE_URL =
            System.getProperty("baseUrl", "http://localhost:8080");

    public static final String ADMIN_USER = "admin";
    public static final String ADMIN_PASS = "Admin@2026";

    public static final String EDITOR_USER = "editor";
    public static final String EDITOR_PASS = "Editor@2026";

    public static final String AUTHOR_USER = "author";
    public static final String AUTHOR_PASS = "Author@2026";

    public static final String CONTRIBUTOR_USER = "contributor";
    public static final String CONTRIBUTOR_PASS = "Contributor@2026";

    public static final String SUBSCRIBER_USER = "subscriber";
    public static final String SUBSCRIBER_PASS = "Subscriber@2026";

    /** 显式等待默认超时（秒） */
    public static final int WAIT_SECONDS = 15;

    private Config() {
    }
}
