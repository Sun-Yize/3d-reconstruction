// pages/recon/recon.js
Page({

  /**
   * 页面的初始数据
   */
  data: {

  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {

  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady: function () {

  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow: function () {

  },

  /**
   * 生命周期函数--监听页面隐藏
   */
  onHide: function () {

  },

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload: function () {

  },

  monocular: function () {
    var _this = this
    wx.showLoading({
      title: '加载中',
    })
    wx.request({
      url: 'https://inifyy.cn:8083/monocular', //仅为示例，并非真实的接口地址
      method: 'GET',
      header: {
        'content-type': 'application/json' // 默认值
      },
      success (res) {
        _this.setData({
          glo_img: "data:image/png;base64," + res.data
        })
        wx.hideLoading()
      },fail (err) {
        wx.hideLoading()
      }
    })
  },

  obj_model: function () {
    var _this = this
    wx.showLoading({
      title: '加载中',
    })
    wx.request({
      url: 'https://inifyy.cn:8083/obj_model', //仅为示例，并非真实的接口地址
      method: 'GET',
      header: {
        'content-type': 'application/json' // 默认值
      },
      success (res) {
        console.log(res)
        wx.downloadFile({
          url: 'https://inifyy.cn:8083/download', //仅为示例，并非真实的资源
          success (res) {
            _this.setData({
              glo_img: res.tempFilePath
            })
          }
        })
        wx.hideLoading()
      },fail (err) {
        wx.hideLoading()
      }
    })
  },
  
})