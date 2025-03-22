<template>
	<div v-if="plans.length">
		<div
			class="bg-gray-0 flex rounded-t-md border border-b-0 px-4 py-3 text-base text-gray-800"
		>
			<div class="w-10"></div>
			<div class="w-1/4">{{ $t('Plan') }}</div>
			<div class="w-1/4">{{ $t('Compute') }}</div>
			<div class="w-1/4">{{ $t('Database') }}</div>
			<div class="w-1/4">{{ $t('Disk') }}</div>
			<div class="w-1/4">{{ $t('Support') }}</div>
		</div>
		<div
			class="focus-within:shadow-outline flex cursor-pointer border px-4 py-3 text-left text-base"
			:class="[
				selectedPlan === plan ? 'bg-gray-100' : 'hover:bg-gray-50',
				{
					'border-b-0': i !== plans.length - 1,
					'rounded-b-md border-b': i === plans.length - 1,
					'pointer-events-none': plan.disabled
				}
			]"
			v-for="(plan, i) in plans"
			:key="plan.name"
			@click="$emit('update:selectedPlan', plan)"
		>
			<div class="flex w-10 items-center">
				<input
					type="radio"
					class="form-radio text-gray-900"
					:checked="selectedPlan === plan"
					@change="e => (selectedPlan = e.target.checked ? plan : null)"
				/>
			</div>
			<div class="w-1/4 text-gray-900" :class="{ 'opacity-25': plan.disabled }">
				<span class="font-semibold">
					{{ $planTitle(plan) }}
				</span>
				<span v-if="plan.price_vnd > 0"> /tháng</span>
			</div>
			<div class="w-1/4 text-gray-700" :class="{ 'opacity-25': plan.disabled }">
				{{ plan.cpu_time_per_day }}
				{{ $plural(plan.cpu_time_per_day, $t('hour'),
								$t('hours')) }} / {{ $t('day') }}
			</div>
			<div class="w-1/4 text-gray-700" :class="{ 'opacity-25': plan.disabled }">
				{{ formatBytes(plan.max_database_usage, 0, 2) }}
			</div>
			<div class="w-1/4 text-gray-700" :class="{ 'opacity-25': plan.disabled }">
				{{ formatBytes(plan.max_storage_usage, 0, 2) }}
			</div>
			<a
				v-if="plan.support_included"
				href="https://cloud.eov.solutions/lien-he/"
				target="_blank"
				class="w-1/4"
			>
				<Tooltip :text="$t('SitePlansTable_content_1')" placement="top">
					<Badge class="hover:cursor-pointer" color="blue" :label="$t('Yes')" />
				</Tooltip>
			</a>
			<div v-else class="w-1/4"></div>
		</div>
	</div>
	<div class="text-center" v-else>
		<Button :loading="true">{{ $t('Loading') }}</Button>
	</div>
</template>

<script>
export default {
	name: 'SitePlansTable',
	props: ['plans', 'selectedPlan'],
	emits: ['update:selectedPlan']
};
</script>
