package edu.qa.wp.tests;

import static org.testng.Assert.assertFalse;
import static org.testng.Assert.assertTrue;

import org.testng.annotations.Test;

import edu.qa.wp.BaseTest;
import edu.qa.wp.Config;
import edu.qa.wp.pages.AdminPage;
import edu.qa.wp.pages.LoginPage;
import io.qameta.allure.Description;
import io.qameta.allure.Epic;
import io.qameta.allure.Feature;
import io.qameta.allure.Severity;
import io.qameta.allure.SeverityLevel;
import io.qameta.allure.Story;

/** 用例集：登录与账号（对应 R01 / TC-AUTH-001~004） */
@Epic("WordPress Web 测试")
@Feature("登录与账号")
public class LoginTest extends BaseTest {

    @Test(priority = 1, description = "TC-AUTH-001 管理员正确凭据登录成功")
    @Story("正向登录")
    @Severity(SeverityLevel.BLOCKER)
    @Description("使用 admin/Admin@2026 登录，应跳转后台并出现管理工具条")
    public void adminLoginSuccess() {
        LoginPage page = new LoginPage(driver).open();
        page.login(Config.ADMIN_USER, Config.ADMIN_PASS);

        AdminPage admin = new AdminPage(driver);
        assertTrue(admin.currentUrl().contains("wp-admin"),
                "登录后应进入后台，实际 URL=" + admin.currentUrl());
        assertTrue(admin.hasAdminBar(), "后台应显示 #wpadminbar 管理工具条");
    }

    @Test(priority = 2, description = "TC-AUTH-002 密码错误时登录失败")
    @Story("负向登录")
    @Severity(SeverityLevel.CRITICAL)
    @Description("正确用户名 + 错误密码，应停留在登录页并给出错误提示")
    public void wrongPasswordRejected() {
        LoginPage page = new LoginPage(driver).open();
        page.login(Config.ADMIN_USER, "wrong-password-999");

        assertFalse(page.currentUrl().contains("wp-admin/edit"),
                "错误密码不应进入后台");
        assertTrue(page.hasError(), "应显示登录错误提示");
        System.out.println("[INFO] 错误提示文案: " + page.errorText());
    }

    @Test(priority = 3, description = "TC-AUTH-004 用户名为空时的校验")
    @Story("边界校验")
    @Severity(SeverityLevel.NORMAL)
    @Description("用户名留空提交，应被拦截并提示，不出现 500")
    public void emptyUsernameRejected() {
        LoginPage page = new LoginPage(driver).open();
        page.login("", "Any@2026");

        assertFalse(page.currentUrl().contains("wp-admin/edit"),
                "空用户名不应进入后台");
        assertTrue(page.currentUrl().contains("wp-login.php"),
                "应停留在登录页，实际 URL=" + page.currentUrl());
        assertTrue(driver.getTitle() != null && !driver.getTitle().isEmpty(),
                "页面不应白屏");
    }
}
