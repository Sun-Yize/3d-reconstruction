// miniprogram/pages/home/home.js
import Notify from '../@vant/weapp/notify/notify';

Page({
  data: {
    changeStyle: false,
    fileList: [],
  },

  afterRead(event) {
    const { fileList = [] } = this.data;
    fileList.push({url: event });
    this.setData({ fileList });
  },

  onLoad: function (options) {

  },

  renewList: function () {
    var tempList = this.data.fileList;
    for (var i=0; i<tempList.length; i++){
      wx.uploadFile({
        url: 'https://inifyy.cn:8083/',
        filePath: tempList[i].url,
        name: 'file',
        formData: {
          'name': i
        },
      })
    }
  },

  choose: function() {
    var _this = this
    if (this.data.fileList.length<9) {
      var count = 9-_this.data.fileList.length;
      wx.chooseImage({
        count: count,
        success (res) {
          for (var i=0;i<res.tempFilePaths.length;i++){
            const { fileList = [] } = _this.data;
            fileList.push({url: res.tempFilePaths[i], deletable: false});
            _this.setData({ fileList });
          }
          _this.renewList()
          Notify({
            type: 'success',
            message: '选择成功',
            duration: 1000,
          });
        }
      })
    }
  },

  scan: function () {
    var obj = JSON.stringify(this.data.fileList)
    if(this.data.fileList.length<1){
      wx.showToast({
        icon: "none",
        title: '请选择图片！',
      })
    // }else if(this.data.fileList.length==1){
    //   wx.navigateTo({
    //     url: '/pages/select/select?obj=' + obj,
    //   })
    }else{
      wx.navigateTo({
        url: '/pages/enhance/enhance?obj=' + obj,
      })
    }
  },

  scan: function () {
    var obj = JSON.stringify(this.data.fileList)
    if(this.data.fileList.length<1){
      wx.showToast({
        icon: "none",
        title: '请选择图片！',
      })
    // }else if(this.data.fileList.length==1){
    //   wx.navigateTo({
    //     url: '/pages/select/select?obj=' + obj,
    //   })
    }else{
      wx.navigateTo({
        url: '/pages/recon/recon'
      })
    }
  },
})