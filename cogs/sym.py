import discord
from discord.ext import commands
import aiohttp
from PIL import Image,ImageOps

import io

def create_sym(image,center):
    """シンメトリーな画像を生成し、BytesIOオブジェクトとして返す。"""
    img = Image.open(image) # 元画像

    l_croped = img.crop((0,0,center,img.height)) # 顔の左半分
    l_mirror = ImageOps.mirror(l_croped) # 左半分を反転した

    l_for_paste = Image.new("RGB",
                            (l_croped.width*2,l_croped.height)) # 合成用画像
    l_for_paste.paste(l_croped,(0,0)) # 左側に元画像の左半分
    l_for_paste.paste(l_mirror,(l_croped.width,0)) # 右側には左半分の反転

    with io.BytesIO() as left_output:
        # BytesIOオブジェクトに変換する処理
        l_for_paste.save(left_output,format="JPEG")
        left_contents = left_output.getvalue()

    r_croped = img.crop((center,0,img.width,img.height)) # 顔の右半分
    r_mirror = ImageOps.mirror(right_croped) # 右半分を反転した

    r_for_paste = Image.new("RGB",
                            (r_croped.width*2,r_croped.height)) # 合成用画像
    r_for_paste.paste(r_mirror,(0,0)) # 左側に右半分の反転
    r_for_paste.paste(r_croped,(r_croped.width,0)) # 右側に元画像の右半分 

    with io.BytesIO() as right_output:
        # BytesIOオブジェクトに変換する処理
        r_for_paste.save(right_output,format="JPEG")
        r_contents = right_output.getvalue()

    return io.BytesIO(left_contents),io.BytesIO(right_contents)

async def get_center(image_url):
    """各顔の中心を返す。"""
    url = "https://faceplusplus-faceplusplus.p.rapidapi.com/facepp/v3/detect"
    query = {"image_url": image_url}

    headers = {
        "x-rapidapi-host": "faceplusplus-faceplusplus.p.rapidapi.com",
        "x-rapidapi-key": "3411560c9fmsh1a24d4f38164377p13eb59jsn9d5a103a64e0",
        "content-type": "application/x-www-form-urlencoded"
    }

    async with aiohttp.ClientSession() as session:
        # botの通信を阻害するため、requestsではなくaiohttpを使う。
        async with session.post(url,params=query,headers=headers) as resp:
            data = await resp.json() #取得したデータ

    if data.get("faces"):
        # もし顔が存在していれば
        centers = []

        for datum in data["faces"]:
            # 各顔の中心をリストに追加
            tmp = datum["face_rectangle"]
            left = tmp["left"]
            width = tmp["width"]

            centers.append(left+(width//2))
    else:
        centers = []

    return centers
    
class Sym(commands.Cog,name="シンメトリー"):
    def __init__(self,bot):
        self.bot = bot
        
    @commands.command()
    async def symmetry(self,ctx):
        """
        添付された人物の画像からシンメトリー画像を生成します。
        """
        if not ctx.message.attachments:
            return
        image = ctx.message.attachments[0]
        
        centers = await get_center(image.url) # 顔の中心のリスト
        true_image = io.BytesIO(await image.read()) # 画像データ

        for center in centers:
            left,right = create_sym(true_image,center) #シンメトリー画像データ

            await ctx.send(files=[discord.File(left,"left.jpg"),
                                  discord.File(right,"right.jpg")])

def setup(bot):
    bot.add_cog(Sym(bot))
