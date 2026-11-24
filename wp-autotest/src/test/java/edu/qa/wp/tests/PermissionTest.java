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

/** 用例集：角色权限（对应 R06 / TC-PERM-001、TC-PERM-002） */
@Epic("WordPress Web 测试")
@Feature("角色与权限")
public class PermissionTest extends BaseTest {

    @Test(priority = 1, description = "TC-PERM-002 订阅者无法进入后台功能页")
    @Story("后台访问控制")
    @Severity(SeverityLevel.CRITICAL)
    @Description("订阅者直访 /wp-admin/edit.php，应被拒绝，且不显示管理工具条")
    public void subscriberCannotEnterAdmin() {
        new LoginPage(driver).open()
                .login(Config.SUBSCRIBER_USER, Config.SUBSCRIBER_PASS);

        driver.get(Config.BASE_URL + "/wp-admin/edit.php");

        AdminPage admin = new AdminPage(driver);
        assertFalse(admin.hasAdminBar(),
                "订阅者不应看到管理工具条，实际 URL=" + admin.currentUrl());
        String body = admin.bodyText();
        assertTrue(body.contains("抱歉") || body.contains("不能") || body.contains("权限"),
                "应显示无权访问提示，实际页面片段：" + body.substring(0, Math.min(160, body.length())));
        System.out.println("[INFO] 订阅者访问后台后 URL: " + admin.currentUrl());
    }

    @Test(priority = 2, description = "TC-PERM-001 投稿者没有“发布”按钮，只能提交审核")
    @Story("发布权限")
    @Severity(SeverityLevel.BLOCKER)
    @Description("投稿者打开新建文章页，应无 #publish 按钮，但存在“提交审核”")
    public void contributorCannotPublish() {
        new LoginPage(driver).open()
                .login(Config.CONTRIBUTOR_USER, Config.CONTRIBUTOR_PASS);

        AdminPage admin = new AdminPage(driver);
        admin.openNewPost().waitForEditor();

        assertFalse(admin.hasPublishButton(),
                "投稿者不应看到“发布”按钮");
        assertTrue(admin.hasSubmitForReviewButton(),
                "投稿者应有“提交审核”按钮");
    }
}
