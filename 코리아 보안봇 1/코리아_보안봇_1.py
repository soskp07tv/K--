import datetime
import discord
from discord import app_commands
from discord.ext import commands

# 1. 봇 권한 및 인텐트 설정
intents = discord.Intents.default()
intents.message_content = True  # 메시지 내용 읽기 권한

bot = commands.Bot(command_prefix="!", intents=intents)


# 2. 봇 준비 완료 및 자동 상태 설정 이벤트
@bot.event
async def on_ready():
    print(f"성공적으로 로그인했습니다: {bot.user}")

    # 봇 상태 및 활동 메시지 설정
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game(name="서버 수호 및 관리 중"),
    )
    print("봇 상태가 '온라인 (서버 수호 및 관리 중)'으로 설정되었습니다.")

    # 슬래시 명령어 동기화
    try:
        synced = await bot.tree.sync()
        print(f"슬래시 명령어 {len(synced)}개 동기화 완료")
    except Exception as e:
        print(f"명령어 동기화 중 오류 발생: {e}")


# 3. @육군 멘션 시 응답 이벤트
@bot.event
async def on_message(message):
    # 봇 메시지 무시 (무한 루프 방지)
    if message.author.bot:
        return

    # '육군' 유저 또는 역할 멘션 확인
    if any(mention.name == "육군" for mention in message.mentions) or any(
        role.name == "육군" for role in message.role_mentions
    ):
        await message.channel.send("```전 언제나 함께 있어요!```")

    await bot.process_commands(message)


# 4. 슬래시 명령어 ( / )

# /밴
@bot.tree.command(name="밴", description="사용자를 서버에서 영구 차단합니다.")
@app_commands.describe(user="차단할 대상", reason="차단 사유")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(
    interaction: discord.Interaction,
    user: discord.Member,
    reason: str = "사유 없음",
):
    await user.ban(reason=reason)
    await interaction.response.send_message(
        f"```{user.display_name} 님을 밴 처리했습니다. (사유: {reason})```"
    )


# /타임아웃
@bot.tree.command(
    name="타임아웃",
    description="사용자를 일정 시간 동안 차단(타임아웃)합니다.",
)
@app_commands.describe(
    user="대상", duration_minutes="차단 시간(분)", reason="사유"
)
@app_commands.checks.has_permissions(moderate_members=True)
async def timeout(
    interaction: discord.Interaction,
    user: discord.Member,
    duration_minutes: int,
    reason: str = "사유 없음",
):
    duration = datetime.timedelta(minutes=duration_minutes)
    await user.timeout(duration, reason=reason)
    await interaction.response.send_message(
        f"```{user.display_name} 님을 {duration_minutes}분 동안 타임아웃 처리했습니다. (사유: {reason})```"
    )


# /킥
@bot.tree.command(
    name="킥", description="사용자를 서버에서 강제 퇴장시킵니다."
)
@app_commands.describe(user="추방할 대상", reason="추방 사유")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(
    interaction: discord.Interaction,
    user: discord.Member,
    reason: str = "사유 없음",
):
    await user.kick(reason=reason)
    await interaction.response.send_message(
        f"```{user.display_name} 님을 킥 처리했습니다. (사유: {reason})```"
    )


# /도배 (메시지 청소)
@bot.tree.command(
    name="도배", description="최근 메시지를 지정한 개수만큼 삭제합니다."
)
@app_commands.describe(amount="삭제할 메시지 개수 (1~100)")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear_spams(interaction: discord.Interaction, amount: int):
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(
        f"```{len(deleted)}개의 메시지를 삭제하여 도배를 정리했습니다.```",
        ephemeral=True,
    )


# /테러 (긴급 방어)
@bot.tree.command(
    name="테러",
    description="서버 테러 상황 시 채널 권한을 긴급 제어합니다.",
)
@app_commands.checks.has_permissions(administrator=True)
async def anti_raid(interaction: discord.Interaction):
    overwrite = interaction.channel.overwrites_for(
        interaction.guild.default_role
    )
    overwrite.send_messages = False
    await interaction.channel.set_permissions(
        interaction.guild.default_role, overwrite=overwrite
    )
    await interaction.response.send_message(
        "```⚠️ 테러 감지! 현재 채널의 메시지 전송 권한을 차단했습니다.```"
    )


# 5. 권한 부족 에러 공통 처리
@ban.error
@timeout.error
@kick.error
@clear_spams.error
@anti_raid.error
async def on_command_error(
    interaction: discord.Interaction, error: app_commands.AppCommandError
):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(
            "```이 명령어를 사용할 권한이 없습니다.```", ephemeral=True
        )


# 6. 봇 실행
# ⚠️ 본인의 디스코드 봇 토큰을 입력하세요.
bot.run("MTU2MDU3NzIzNTQ3NDQ0ODM4NQ.GTMLK_.6El3YAmvvPKhsa02d3ivTwlXDQF0uReCDkDFpg")
