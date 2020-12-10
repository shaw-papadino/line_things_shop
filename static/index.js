$(function () {
    // 送信
    $('form').submit(function () {
        let msg = "送信しました";
        sendText(msg);

        return false;
    });
});
