// pages/enhance/enhance.js
import Notify from '../@vant/weapp/notify/notify';

Page({

  /**
   * 页面的初始数据
   */
  data: {
    index: 0,
    type: 0,
    glo_img: '',

  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    var obj =JSON.parse(options.obj)
    this.setData({
      fileList: obj
    })
    console.log(this.data.fileList)
    this.showimg()
  },

  showimg: function () {
    var _this = this
    wx.showLoading({
      title: '加载中',
    })
    wx.request({
      url: 'https://inifyy.cn:8083/', //仅为示例，并非真实的接口地址
      method: 'GET',
      data: {
        img_index: _this.data.index,
        img_type: _this.data.type,
      },
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

  saveimg: function () {
    Notify({
      type: 'success',
      message: '保存成功',
      duration: 1000,
    });
  },

  sharp: function () {
    this.setData({
      type: 0,
    })
    this.showimg()
  },

  enhance: function () {
    this.setData({
      type: 1,
    })
    this.showimg()
  },

  black_white: function () {
    this.setData({
      type: 2,
    })
    this.showimg()
  },

  before_img: function () {
    var _this = this
    if(this.data.index>0){
      this.setData({
        index: _this.data.index-1,
      })
      this.showimg()
    }
    console.log(1)
  },

  after_img: function () {
    var _this = this
    if(this.data.index < this.data.fileList.length-1){
      this.setData({
        index: _this.data.index+1,
      })
      this.showimg()
    }
  },

})