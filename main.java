package org.oristool.eulero;

import org.oristool.eulero.modeling.Activity;
import org.oristool.eulero.modeling.ModelFactory;
import org.oristool.eulero.modeling.Simple;
import org.oristool.eulero.modeling.stochastictime.UniformTime;
import org.oristool.eulero.evaluation.heuristics.SDFHeuristicsVisitor;
import org.oristool.eulero.evaluation.approximator.TruncatedExponentialMixtureApproximation;
import org.oristool.eulero.ui.ActivityViewer;
import org.oristool.eulero.evaluation.heuristics.EvaluationResult;


import java.math.BigDecimal;
import java.math.BigInteger;
import java.util.List;

/**
 * This is an example file to demonstrate the basic usage of the Eulero library.
 */
public class main {

    public static void main(String[] args) {
        // 1. Define the stochastic time for the activities.
        // For this example, we use a uniform distribution between 1 and 2 time units.
        UniformTime uniformTime = new UniformTime(BigDecimal.ONE, BigDecimal.valueOf(2));

        // 2. Create simple activities.
        // These are the basic building blocks of our model.
        Activity activityA = new Simple("A", uniformTime.clone());
        Activity activityB = new Simple("B", uniformTime.clone());
        Activity activityC = new Simple("C", uniformTime.clone());

        // 3. Build a complex workflow (DAG) by composing the simple activities.
        // This model represents activity A followed by B and C running in parallel.
        Activity model = ModelFactory.sequence(
            activityA,
            ModelFactory.forkJoin(activityB, activityC)
        );

        // 4. Set up the analysis visitor.
        // This defines the strategy to analyze the model.
        // We use a "Split Dependencies First" heuristic here.
        SDFHeuristicsVisitor analyzer = new SDFHeuristicsVisitor(
            BigInteger.valueOf(4), // CThreshold: Concurrency threshold
            BigInteger.TEN,      // QThreshold: Sequence degree threshold
            new TruncatedExponentialMixtureApproximation()
        );

        // 5. Analyze the model.
        // We calculate the Cumulative Distribution Function (CDF) of the completion time.
        BigDecimal timeLimit = model.max(); // Analyze up to the maximum possible completion time
        BigDecimal timeStep = model.getFairTimeTick(); // Use a reasonable time step

        System.out.println("Analyzing model: " + model.name());
        System.out.println("Time limit: " + timeLimit);
        System.out.println("Time step: " + timeStep);

        double[] cdf = model.analyze(timeLimit, timeStep, analyzer);

        // 6. Display the results.
        System.out.println("Analysis complete. CDF values:");
        for (int i = 0; i < cdf.length; i++) {
            System.out.printf("Time: %.2f, CDF: %.4f%n", i * timeStep.doubleValue(), cdf[i]);
        }

        // You can also use the ActivityViewer to plot the results.
        // Note: This will open a Swing GUI window.
        EvaluationResult result = new EvaluationResult("Example Model", cdf, 0, cdf.length, timeStep.doubleValue(), 0);
        ActivityViewer.CompareResults("Example Analysis", List.of("CDF"), List.of(result));
    }
}
