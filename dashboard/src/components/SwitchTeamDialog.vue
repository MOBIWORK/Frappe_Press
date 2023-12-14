<template>
	<Dialog :options="{ title: 'Chuyển đổi nhóm' }">
		<template v-slot:body-content>
			<span class="text-xs text-gray-600"
				>Nhóm hiện tại: {{ $account.team.name }}</span
			>
			<div class="my-2 border-t">
				<ListItem
					v-for="team in $account.teams"
					:title="`${team.team_title}`"
					:description="team.user"
					:key="team"
				>
					<template #actions>
						<div v-if="$account.team.name === team.name">
							<Badge label="Active" theme="blue" />
						</div>
						<div v-else class="flex flex-row justify-end">
							<Button @click="$account.switchToTeam(team.name)">
								Chuyển đổi
							</Button>
						</div>
					</template>
				</ListItem>
			</div>
		</template>
	</Dialog>
</template>

<script>
export default {
	name: 'SwitchTeamDialog'
};
</script>
