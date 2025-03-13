<template>
	<Dialog :options="{ title: $t('switch_team') }">
		<template v-slot:body-content>
			<span class="text-xs text-gray-600"
				>{{ $t('Current Team') }}: {{ $account.team.team_title }}</span
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
								{{ $t('Switch') }}
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
