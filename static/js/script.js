$(document).ready(function(){
  /**
  predict API を Ajax で叩く
  */
  function predict() {
    // 叩くAPIのURL
    var baseURL = '/predict';

    //取得した引数を格納
    var data = {
      screen_name : $("#screen_name").val(),
      n : $("#n").val(),
      access_token : $("#access_token").val(),
      access_token_secret : $("#access_token_secret").val()
    };

    // screen_name が入力されているか
    if(!data.screen_name) {
      editModal(
        'Error',
        'screen_name を入力して下さい．' +
        modalButtons()
      );
      return;
    }

    // APIを叩く
    $.ajax({
      type: "GET",
      url: baseURL, //APIのURL
      data: data, //入力データ
      dataType: 'json',
      timeout: 28000,
      success: function(response) {//叩いた結果がresponseに格納されている
        // エラーの場合
        if('error_msg' in response) {
          editModal(
            'Error',
            response.error_msg +
            modalButtons()
          );
          return;
        }

        if (response.predicted_tweet !== null){
          editModal(
            'Prediction Results.',
            '<div class="panel panel-default" id="panel-tweet">' +
              '<div class="panel-body">' +
                '<a href="https://twitter.com/' + response.screen_name + '" target="_blank" class="media">' +
                  '<div class="media-left">' +
                    '<img class="media-object img-rounded" src="' + response.profile_image_url_https + '" alt="' + response.name + '" width="48px" height="48px">' +
                  '</div>' +
                  '<div class="media-body">' +
                    '<h4 class="media-heading">' + response.name + '</h4>' +
                    '<span class="twitter-gray">@' + response.screen_name + '</span>' +
                  '</div>' +
                '</a>' +
                '<p>' +
                  response.predicted_tweet +
                '</p>' +
                '<p class="twitter-gray time">' +
                  response.time +
                '</p>' +
                '<p class="twitter-gray">' +
                  '<i class="fa fa-reply"></i>&ensp;&ensp;&ensp;&ensp;' +
                  '<i class="fa fa-retweet"></i>&ensp;&ensp;&ensp;&ensp;' +
                  '<i class="fa fa-star"></i>' +
                '</p>' +
              '</div>' +
            '</div>' +
            modalButtons(response.predicted_tweet)
          );
        }
        else{
          editModal(
            'Error',
            'Somothing wrong... Please try to reload blowser.' +
            modalButtons()
            );
        }
      },

      error: function(XMLHttpRequest, textStatus, errorThrown) {
          editModal(
            'Error',
            'タイムアウトしました．やり直して下さい．<br>' +
            'error_msg: ' + errorThrown +
            modalButtons()
          );
      }
    });
  }

  /**
   * Modal に表示するボタンを生成
   */
  function modalButtons(predicted_tweet) {
    var buttons = '<div class="text-center modal-button-box">';

    if(predicted_tweet) {
      buttons += '<a href="http://twitter.com/share?count=horizontal&amp;original_referer=https://tweet-predictor.herokuapp.com/&amp;url=https://tweet-predictor.herokuapp.com/&amp;text=' + predicted_tweet.replace(/[\n\r]/g,"") + '&amp;hashtags=TweetPredictor" onclick="window.open(this.href, \'tweetwindow\', \'width=550, height=450, personalbar=0, toolbar=0, scrollbars=1, resizable=1\'); return false;">' +
                 '<button class="btn btn-default">' +
                 '<i class="fa fa-twitter"></i>&ensp;結果をツイートする' +
                 '</button>' +
                 '</a>' +
                 '<button class="btn btn-primary btn-predict">' +
                 '<i class="fa fa-paper-plane"></i> もういちど！' +
                 '</button>';
    }

    buttons += '<button type="button" data-dismiss="modal" aria-hidden="true" class="btn btn-success">' +
               '&times; とじる' +
               '</button>' +
               '</div>';

    return buttons;
  }

  /**
   * modal の内容変更
   */
  function editModal(title, body) {
    $('.modal-title').fadeOut('fast', function() {
      $('.modal-title').html(title);
    });
    $('.modal-body').fadeOut('fast', function() {
      $('.modal-body').html(body);
    });
    $('.modal-title').fadeIn('fast');
    $('.modal-body').fadeIn('fast');
  }

  /**
   * modal を表示
   */
  function showModal(title, body) {
    editModal(title, body);
    $('#modal').modal('show');
  }

  /* [詳細設定] を押した時 */
  $("#toggle_settings").on('click', function() {
    $(".settings").fadeIn('slow').css("display","inline-block");
    $("#toggle_settings").fadeOut('slow');
  });

  /* Predict を押した時 */
  $(document).on('click', '.btn-predict', function() {
    // Modal 表示
    showModal(
      'Now predicting...',
      '<div class="text-center">' +
        '<p><i class="fa fa-spinner fa-pulse fa-5x"></i></p>' +
        '<p class="twitter-gray">ツイート生成には最大30秒程度かかります</p>' +
      '</div>'
    );

    predict();
  });
});